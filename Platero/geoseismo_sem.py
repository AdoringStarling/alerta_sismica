import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import timedelta

#Función para encontrar número máximo de sismos registrados diarios por rango de magnitud
def max_sismos_diarios(m0): 
    conteo=0
    for i in m0['UTC']:
        long = len(m0[(m0['UTC']<=i)&(m0['UTC']>=i- timedelta(hours=24))])
        if conteo<long:
            conteo=long
    return conteo


def cylinder(r, h,x0,y0,a =0, nt=600, nv=50):
    """
    r=radio
    h=altura
    a=altura sobre eje x y y (z)
    nt=Calidad en un eje
    nv=Calidad e otro eje
    x=coordenada x
    y=coordenada y
    """
    theta = np.linspace(0, 2*np.pi, nt)
    v = np.linspace(a, a+h, nv )
    theta, v = np.meshgrid(theta, v)
    x = r*np.cos(theta)+x0
    y = r*np.sin(theta)+y0
    z = v
    return x, y, z

def boundary_circle(r, h,x0,y0, nt=600):
    """
    r - radio del borde
    h - altura sobre el eje xy (z)
    nt-calidad de un eje
    x0-coordenada x
    y0-coordenada y
    """
    theta = np.linspace(0, 2*np.pi, nt)
    x= r*np.cos(theta)+x0
    y = r*np.sin(theta)+y0
    z = h*np.ones(theta.shape)
    return x, y, z

def volumen_semaforo(r1,a1,h1,x01,y01,opac,col_cyl,col_cir,name):
    x1, y1, z1 = cylinder(r1, h1,x01,y01, a=a1)
    cyl1 = go.Surface(x=x1, y=y1, z=z1,
                    colorscale = col_cyl,
                    showscale=False,
                    opacity=opac,
                    name=name)
    xb_low, yb_low, zb_low = boundary_circle(r1, a1,x01,y01)
    xb_up, yb_up, zb_up = boundary_circle(r1, a1+h1,x01,y01)

    bcircles1 =go.Scatter3d(x = xb_low.tolist()+[None]+xb_up.tolist(),
                            y = yb_low.tolist()+[None]+yb_up.tolist(),
                            z = zb_low.tolist()+[None]+zb_up.tolist(),
                            mode ='lines',
                            line = dict(color=col_cir, width=2),
                            opacity =0.55, showlegend=False,
                            name=name)
    return cyl1,bcircles1

def var_un(x_pozo_inv_kale, y_pozo_inv_kale,h_pozo_inv_kale_m,sismos,nam,wgs84):    
    #Se importan los datos de los pozos del proyecto Kalé

    # x_pozo_inv_kale, y_pozo_inv_kale  = 4905500, 2371970
    # h_pozo_inv_kale_m = 3902 #m
    r_ext = 2*h_pozo_inv_kale_m+20000 #m

    geo_inv=wgs84.transform(y_pozo_inv_kale ,x_pozo_inv_kale)

    kale= go.Scatter3d(
        x=np.array(geo_inv[1]),
        y=np.array(geo_inv[0]),
        z=np.array(300),
        mode='markers',
        marker_symbol='diamond',
        name=nam,
        hovertemplate ="PPII Kalé",
        marker=dict(
            size=4,
            color='black'
        )
    )

    r1=2*h_pozo_inv_kale_m

    geo_r1=wgs84.transform(y_pozo_inv_kale+r1,x_pozo_inv_kale)
    geo_r2=wgs84.transform(y_pozo_inv_kale+r_ext,x_pozo_inv_kale)
    geo_r3=wgs84.transform(y_pozo_inv_kale+50000,x_pozo_inv_kale)

    #Volumen de suspension
    cyl1,bcircles1=volumen_semaforo(geo_r1[0]-geo_inv[0] ,0,-16000,
                        geo_inv[1],geo_inv[0],0.5,
                        ['red','red'],'red','Suspensión')
    #Volumen de monitoreo
    cyl2,bcircles2=volumen_semaforo(geo_r2[0]-geo_inv[0],0,-16000,
                        geo_inv[1],geo_inv[0],0.7,
                        ['green','orange'],'green','Monitoreo')
    #Volumen externo
    cyl3,bcircles3=volumen_semaforo(geo_r3[0]-geo_inv[0],0,-32000,
                        geo_inv[1],geo_inv[0],0.3,
                        ['aqua','aqua'],'blue','Externo')





    sismos_local = sismos[(sismos['PROF. (Km)']<=16)&
                    ((((sismos['ESTE']-x_pozo_inv_kale)**2)+
                    ((sismos['NORTE']-y_pozo_inv_kale)**2))
                    **(1/2)<=r_ext)]

    #Drenajes
    # df_rivers=pd.read_csv('datasets\drenajes.csv')
    Mc=1.8

    m0 = sismos[(sismos['MAGNITUD']<Mc)]
    m1 = sismos[(sismos['MAGNITUD']>=Mc)&(sismos['MAGNITUD']<2)]
    m2 = sismos[(sismos['MAGNITUD']>=2)&(sismos['MAGNITUD']<3)]
    m3 = sismos[(sismos['MAGNITUD']>=3)&(sismos['MAGNITUD']<4)]
    m4 = sismos[(sismos['MAGNITUD']>=4)]
    mn=(m0,m1,m2,m3,m4)
    # Cálculo de parámetros para el semáforo

    nmsod_m0 = max_sismos_diarios(m0)   #Número máximo de sismos observados diarios
    nmsod_m1 = max_sismos_diarios(m1)   #Número máximo de sismos observados diarios
    nmsod_m2 = max_sismos_diarios(m2)   #Número máximo de sismos observados diarios
    nmsod_m3 = max_sismos_diarios(m3)   #Número máximo de sismos observados diarios
    nmsod_m4 = max_sismos_diarios(m4)   #Número máximo de sismos observados diarios
    nmsod_mn=(nmsod_m0,nmsod_m1,nmsod_m2,nmsod_m3,nmsod_m4)
    ND = (sismos['UTC'].max()-sismos['UTC'].min()).days  #Número de días calendario del catálogo

    npsed_m0 = m0.shape[0]/ND    #Número promedio de sismos esperados diarios #OJO!!!!!!!!!
    npsod_m1 = m1.shape[0]/ND   #Número promedio de sismos observados diarios
    npsod_m2 = m2.shape[0]/ND   #Número promedio de sismos observados diarios
    npsod_m3 = m3.shape[0]/ND   #Número promedio de sismos observados diarios
    npsod_m4 = m4.shape[0]/ND   #Número promedio de sismos observados diarios
    npseod_mn=(npsed_m0,npsod_m1,npsod_m2,npsod_m3,npsod_m4)

    if nmsod_m1 == npsod_m1:
            d_m1 = 1 - (1/ND)
    else:
        d_m1 = (nmsod_m1/npsod_m1)/2 #Tolerancia frecuencial m1    

    if nmsod_m2 == npsod_m2:
        d_m2 = 1 - (1/ND)
    else:
        d_m2 = (nmsod_m2/npsod_m2)/2 #Tolerancia frecuencial m2
        
    if nmsod_m3 == npsod_m3:
        d_m3 = 1 - (1/ND)
    else:
        d_m3 = (nmsod_m3/npsod_m3)/2 #Tolerancia frecuencial m3

    if nmsod_m4 == npsod_m4:
        d_m4 = 1 - (1/ND)
    else:
        d_m4 = (nmsod_m4/npsod_m4)/2 #Tolerancia frecuencial m4
    d_mn=(d_m1,d_m2,d_m3,d_m4)

    xe=x_pozo_inv_kale+52000
    xw=x_pozo_inv_kale-52000
    ys=y_pozo_inv_kale-52000
    yn=y_pozo_inv_kale+52000

    ge=wgs84.transform(ys,xe)[1]
    gw=wgs84.transform(yn,xw)[1]
    gn=wgs84.transform(yn,xe)[0]
    gs=wgs84.transform(ys,xw)[0]

    sismos_total = sismos[(sismos['PROF. (Km)']<=32)&
                    (sismos['ESTE']<=xe)&
                    (sismos['ESTE']>=xw)&
                    (sismos['NORTE']<=yn)&
                    (sismos['ESTE']>=ys)]
    return kale,nam,geo_inv,cyl1,bcircles1,cyl2,bcircles2,cyl3,bcircles3,sismos_total,sismos_local,ND,mn,nmsod_mn,npseod_mn,d_mn,x_pozo_inv_kale,y_pozo_inv_kale

def table_semaforo(sismos_dia,nmsod_mn,npseod_mn,d_mn,Mc,x_pozo_inv_kale,y_pozo_inv_kale,r1):
    m0d = sismos_dia[(sismos_dia['MAGNITUD']<Mc)]
    m1d = sismos_dia[(sismos_dia['MAGNITUD']>=Mc)&(sismos_dia['MAGNITUD']<2)]
    m2d = sismos_dia[(sismos_dia['MAGNITUD']>=2)&(sismos_dia['MAGNITUD']<3)]
    m3d = sismos_dia[(sismos_dia['MAGNITUD']>=3)&(sismos_dia['MAGNITUD']<4)]
    m4d = sismos_dia[(sismos_dia['MAGNITUD']>=4)]
    m4da=m4d [((((m4d ['ESTE']-x_pozo_inv_kale)**2)+
                ((m4d ['NORTE']-y_pozo_inv_kale)**2))
                        **(1/2)<=r1)]
    m4db=m4d [((((m4d ['ESTE']-x_pozo_inv_kale)**2)+
                ((m4d ['NORTE']-y_pozo_inv_kale)**2))
                        **(1/2)>r1)]
    # nmsod_m0,nmsod_m1,nmsod_m2,nmsod_m3,nmsod_m4=nmsod_mn
    npsed_m0,npsod_m1,npsod_m2,npsod_m3,npsod_m4=npseod_mn
    d_m1,d_m2,d_m3,d_m4=d_mn

    nsrd_m0 = len(m0d) #Número de sismos registrados diarios
    nsrd_m1 = len(m1d)
    nsrd_m2 = len(m2d)
    nsrd_m3 = len(m3d)
    nsrd_m4a = len(m4da)
    nsrd_m4b = len(m4db)


    #Semáforo para m0
    d_m0=1 #OJO!!!!!!!!!
    if nsrd_m0 == 0:
        m0c='Verde'
    elif nsrd_m0 > 0 & nsrd_m0 <= npsed_m0+d_m0:
        m0c='Verde'
    elif nsrd_m0 > npsed_m0+d_m0 & nsrd_m0 <= npsed_m0+2*d_m0:
        m0c='Verde'
    elif nsrd_m0 > npsed_m0+2*d_m0 & nsrd_m0 <= npsed_m0+3*d_m0:
        m0c='Verde'
    elif nsrd_m0 > npsed_m0+3*d_m0 & nsrd_m0 <= npsed_m0+4*d_m0:
        m0c='Verde'
    elif nsrd_m0 > npsed_m0+4*d_m0:
        m0c='Amarillo'   
        
    #Semáforo para m1

    if nsrd_m1 == 0:
        m1c='Verde'
    elif nsrd_m1 > 0 & nsrd_m1 <= npsod_m1+d_m1:
        m1c='Verde'
    elif nsrd_m1 > npsod_m1+d_m1 & nsrd_m1 <= npsod_m1+2*d_m1:
        m1c='Verde'
    elif nsrd_m1 > npsod_m1+2*d_m1 & nsrd_m1 <= npsod_m1+3*d_m1:
        m1c='Verde'
    elif nsrd_m1 > npsod_m1+3*d_m1 & nsrd_m1 <= npsod_m1+4*d_m1:
        m1c='Amarillo'
    elif nsrd_m1 > npsod_m1+4*d_m1:
        m1c='Amarillo'
        
    #Semáforo para m2

    if nsrd_m2 == 0:
        m2c='Verde'
    elif nsrd_m2 > 0 & nsrd_m2 <= npsod_m2+d_m2:
        m2c='Verde'
    elif nsrd_m2 > npsod_m2+d_m2 & nsrd_m2 <= npsod_m2+2*d_m2:
        m2c='Verde'
    elif nsrd_m2 > npsod_m2+2*d_m2 & nsrd_m2 <= npsod_m2+3*d_m2:
        m2c='Amarillo'
    elif nsrd_m2 > npsod_m2+3*d_m2 & nsrd_m2 <= npsod_m2+4*d_m2:
        m2c='Amarillo'
    elif nsrd_m2 > npsod_m2+4*d_m2:
        m2c='Naranja'
        
    #Semáforo para m3

    if nsrd_m3 == 0:
        m3c='Verde'
    elif nsrd_m3 > 0 & nsrd_m3 <= npsod_m3+d_m3:
        m3c='Verde'
    elif nsrd_m3 > npsod_m3+d_m3 & nsrd_m3 <= npsod_m3+2*d_m3:
        m3c='Amarillo'
    elif nsrd_m3 > npsod_m3+2*d_m3 & nsrd_m3 <= npsod_m3+3*d_m3:
        m3c='Amarillo'
    elif nsrd_m3 > npsod_m3+3*d_m3 & nsrd_m3 <= npsod_m3+4*d_m3:
        m3c='Naranja'
    elif nsrd_m3 > npsod_m3+4*d_m3:
        m3c='Naranja'
        
    #Semáforo para m4
    m4cb='Verde'
    if nsrd_m4a == 0 and nsrd_m4b == 0:    #Caso a y b: Dentro del volumen de monitoreo o suspensión
        m4ca='Verde'
        m4cb='Verde'
    elif nsrd_m4b > 0 and nsrd_m4b <= npsod_m4+d_m4:    #Caso b: Dentro del volumen de monitoreo
        m4cb='Amarillo'
    elif nsrd_m4b > npsod_m4+d_m4 and nsrd_m4b <= npsod_m4+2*d_m4:  #Caso b: Dentro del volumen de monitoreo
        m4cb='Amarillo'
    elif nsrd_m4b > npsod_m4+2*d_m4 and nsrd_m4b <= npsod_m4+3*d_m4:    #Caso b: Dentro del volumen de monitoreo
        m4cb='Naranja'
    elif nsrd_m4b > npsod_m4+3*d_m4 and nsrd_m4b <= npsod_m4+4*d_m4:    #Caso b: Dentro del volumen de monitoreo
        m4cb='Naranja'
    elif nsrd_m4b > npsod_m4+4*d_m4: #Caso b: Dentro del volumen de monitoreo
        m4cb='Naranja'
    elif nsrd_m4a >= 1:  #Caso a: Dentro del volumen de suspensión 
        m4ca='Rojo'

    mnc=(m0c,m1c,m2c,m3c,m4ca,m4cb)
    nsrd_mn=(nsrd_m0,nsrd_m1,nsrd_m2,nsrd_m3,nsrd_m4a,nsrd_m4b)
    return mnc,nsrd_mn

def semaforo_sismico(sismos_local,Mc,ND,mn,nmsod_mn,npseod_mn,d_mn,x_pozo_inv_kale,y_pozo_inv_kale,r1,r_ext,time=0):
    if time==0:
        time=pd.to_datetime(sismos_local['UTC'].max())
    else:
        time=pd.to_datetime(time)
    sismos_dia = sismos_local[(sismos_local['UTC']<=time)&(sismos_local['UTC']>=time- timedelta(hours=24))]
    sismos_mes = sismos_local[(sismos_local['UTC']<=time)&(sismos_local['UTC']>=time- timedelta(days=30))]
    mnc,nsrd_mn=table_semaforo(sismos_dia,nmsod_mn,npseod_mn,d_mn,Mc,x_pozo_inv_kale,y_pozo_inv_kale,r1)
    m0c,m1c,m2c,m3c,m4ca,m4cb=mnc
    nsrd_m0,nsrd_m1,nsrd_m2,nsrd_m3,nsrd_m4a,nsrd_m4b=nsrd_mn
    mnd=[m0c,m1c,m2c,m3c,m4ca,m4cb]
    if np.isin('Rojo', mnd):
        col='Rojo'
    elif np.isin('Naranja', mnd):
        col='Naranja'
    elif np.isin('Amarillo', mnd):
        col='Amarillo'
    else :
        col='Verde'
    #-------------------Caclulo a mes-----------------------
    timem=pd.to_datetime(sismos_mes['UTC'].max())
    punt=[]
    if len(sismos_mes)>1:
        for _ in range(30):
            sismos_diam = sismos_mes[(sismos_mes['UTC']<=timem)&(sismos_mes['UTC']>=timem- timedelta(hours=24))]
            timem=timem- timedelta(hours=24)
            mnc,_=table_semaforo(sismos_diam,nmsod_mn,npseod_mn,d_mn,Mc,x_pozo_inv_kale,y_pozo_inv_kale,r1)
            m0cm,m1cm,m2cm,m3cm,m4cam,m4cbm=mnc
            mncm=[m0cm,m1cm,m2cm,m3cm,m4cam,m4cbm]
            if np.isin('Naranja', mncm):
                punt.append(3)
            elif np.isin('Amarillo', mncm):
                punt.append(1)
            else :
                punt.append(0)
        puntn=np.sum(punt)
    else:
        puntn=0
    
    Mc=round(Mc,2)
            
    
    dat={'Magnitud': ['m4a', 'm4b','m3','m2','m1','m0'], 
        'Ml': ['>=4', '>=4','[3,4)','[2,3)',f'[{Mc},2]',f'<{Mc}'],
        'NSRD': [nsrd_m4a, nsrd_m4b,nsrd_m3,nsrd_m2,nsrd_m1,nsrd_m0],
        'Semaforo': [m4ca, m4cb,m3c,m2c,m1c,m0c],}
    return pd.DataFrame(data=dat),col,puntn,sismos_dia,sismos_mes