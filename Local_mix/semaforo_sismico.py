from geoseismo_sem import *
import dash
import dash_bootstrap_components as dbc
from dash import html, dash_table
from dash import dcc
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import pyproj

white_button_style = {'background-color': 'white',
                      'color': 'black',
                      'height': '60px',
                      'width': '300px',}

red_button_style = {'background-color': 'red',
                    'color': 'white',
                    'height': '60px',
                    'width': '300px',}

#Poblaciones
df_poblaciones=pd.read_csv('datasets/poblaciones.csv',usecols=['Name','lon','lat','outputSRTM1'])
Poblaciones = go.Scatter3d(
    x=df_poblaciones['lon'],
    y=df_poblaciones['lat'],
    z=df_poblaciones['outputSRTM1']+10, #Conseguir alturas
    mode='markers',
    name="Población",
    marker_symbol='square',
    hovertemplate =df_poblaciones['Name'],
    marker=dict(
        size=6,
        color='red'
    ),
    textposition="bottom right"
)
Pobl=[]
for name,lon,lat,alt in zip(df_poblaciones['Name'],df_poblaciones['lon'],
df_poblaciones['lat'],df_poblaciones['outputSRTM1']):
    un=dict(
            showarrow=False,
            x=lon,
            y=lat,
            z=alt+10,
            text=name,
            xanchor="left",
            xshift=10,
            opacity=0.7,
            font=dict(
                color="black",
                size=12
            ))
Pobl.append(un)

#metricas a WGS84
wgs84 = pyproj.Transformer.from_crs("epsg:9377", "epsg:4326")
#WGS84 A Metricas
magnas = pyproj.Transformer.from_crs("epsg:4326", "epsg:9377")

sismos = pd.read_csv(r'datasets\reporte_LBG.csv')
sismos['FECHA - HORA UTC']=sismos['Fecha  (UTC)'].astype(str)+' '+sismos['Hora  (UTC)'].astype(str)
sismos.rename(columns = {'Latitud(°)':'LATITUD (°)', 
                        'Longitud(°)':'LONGITUD (°)',
                        'Profundidad(Km)':'PROF. (Km)',
                        'Magnitud':'MAGNITUD',
                        'Tipo Magnitud':'TIPO MAGNITUD',
                        'Rms(Seg)':'RMS (Seg)',
                        'Gap(°)':'GAP (°)',
                        'Error  Latitud(Km)':'ERROR LATITUD (Km)',
                        'Error  Longitud(Km)':'ERROR LONGITUD (Km)',
                        'Error  Profundidad(Km)':'ERROR PROFUNDIDAD (Km)'}, 
                        inplace = True)
sismos.drop(['Fecha  (UTC)','Hora  (UTC)'],axis=1,inplace=True)
dfp=magnas.transform(sismos['LATITUD (°)'], sismos['LONGITUD (°)'])
sismos['ESTE'] =dfp[1]
sismos['NORTE']=dfp[0]
sismos['UTC']=pd.to_datetime(sismos['FECHA - HORA UTC'])
cey=wgs84.transform(sismos['NORTE']+(sismos['ERROR LATITUD (Km)']*1000),sismos['ESTE'])[0]
cex=wgs84.transform(sismos['NORTE'],sismos['ESTE']+(sismos['ERROR LONGITUD (Km)']*1000))[1]
sismos['ERROR LONGITUD (°)']=cex-sismos['LONGITUD (°)']
sismos['ERROR LATITUD (°)']=cey-sismos['LATITUD (°)']


#Se importan los datos de los pozos del proyecto Kalé

x_pozo_inv_kale, y_pozo_inv_kale  = 4905500, 2371970
h_pozo_inv_kale_m = 3902 #m

x_pozo_iny_kale, y_pozo_iny_kale  = 4905440, 2371890
h_pozo_iny_kale_m = 2618.232#m

x_pozo_inv_plat, y_pozo_inv_plat  = 4901360, 2360010
h_pozo_inv_plat_m = 3227.8 #m

x_pozo_iny_plat, y_pozo_iny_plat  = 4901300, 2359950
h_pozo_iny_plat_m = 2325.6#m

gw=-74.36650535401542
ge=-73.384852230196
gs=6.785608789773128
gn=7.836724863369543

sismos= sismos[(sismos['PROF. (Km)'] <= 32) &
                      (sismos['LONGITUD (°)'] <= ge) &
                      (sismos['LONGITUD (°)'] >= gw) &
                      (sismos['LATITUD (°)'] <= gn) &
                      (sismos['LATITUD (°)'] >= gs)]

#Investigacion Kale
kale2,nam2,geo_inv2,cyl12,bcircles12,cyl22,bcircles22,cyl32,bcircles32,sismos_local2,ND2,mn2,nmsod_mn2,npseod_mn2,d_mn2,x_pozo_inv_kale2,y_pozo_inv_kale2,r12,r_ext2=var_un(x_pozo_inv_kale, y_pozo_inv_kale,h_pozo_inv_kale_m,sismos,'PPII Kalé - Investigación',wgs84)
#Inyector Kale
kale1,nam1,geo_inv1,cyl11,bcircles11,cyl21,bcircles21,cyl31,bcircles31,sismos_local1,ND1,mn1,nmsod_mn1,npseod_mn1,d_mn1,x_pozo_inv_kale1,y_pozo_inv_kale1,r11,r_ext1=var_un(x_pozo_iny_kale, y_pozo_iny_kale,h_pozo_iny_kale_m,sismos,'PPII Kalé - Inyector',wgs84)
#Investigacion platero
kale4,nam4,geo_inv4,cyl14,bcircles14,cyl24,bcircles24,cyl34,bcircles34,sismos_local4,ND4,mn4,nmsod_mn4,npseod_mn4,d_mn4,x_pozo_inv_kale4,y_pozo_inv_kale4,r14,r_ext4=var_un(x_pozo_inv_plat, y_pozo_inv_plat,h_pozo_inv_plat_m,sismos,'PPII Platero - Investigación',wgs84)
#Iyector platero
kale3,nam3,geo_inv3,cyl13,bcircles13,cyl23,bcircles23,cyl33,bcircles33,sismos_local3,ND3,mn3,nmsod_mn3,npseod_mn3,d_mn3,x_pozo_inv_kale3,y_pozo_inv_kale3,r13,r_ext3=var_un(x_pozo_iny_plat, y_pozo_iny_plat,h_pozo_iny_plat_m,sismos,'PPII Platero- Inyector',wgs84)
# -74.32929781241609 -73.384852230196 6.893917274978344 7.836724863369543

Mc=1.8
#Se cargan los datos de elevacion estos fueron descargados en https://portal.opentopography.org/datasets
# Global Bathymetry and Topography at 15 Arc Sec: SRTM15+ V2.1  
df_topo =pd.read_csv('datasets\local_100m.xyz',delimiter=' ',header=None,decimal='.')
#df_topo =df_topo[(df_topo[1]>gs)&(df_topo[1]<gn)&(df_topo[0]>gw)&(df_topo[0]<ge)] #Filtros previos
mesh_topo = (df_topo.pivot(index=1, columns=0,values=2))
z_topo,x_topo,y_topo=mesh_topo.values,mesh_topo.columns,mesh_topo.index

df_rivers=pd.read_csv('datasets/drenajes_gmrt_WGS84_locales.csv',delimiter=',',decimal='.')


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])

#Cargars los datos

card_main=dbc.Card(
    dbc.CardBody([
                dbc.Nav([
                dbc.NavLink("Inicio", href="https://www.centrodetransparenciappii.org/", active="exact"),
                dbc.NavLink("Modelo 3D VMM", href="https://pinguinodigital.com/wp-content/uploads/2020/08/pagina-en-construcci%C3%B3n1.jpg", active="exact"),
                dbc.NavLink("Semáforo sísmico", href="", active="exact"),]),
                html.H2("Semáforo sísmico", className="card-title"),
                dbc.CardImg( id='SEM',bottom=True, alt='Semaforo',),
                html.H4("Pozo:", className="card-subtitle"),
                dcc.Dropdown(id='POZO',
                        placeholder="Variables a desplegar...",
                        style={'color': 'black'},
                        options=[
                            {'label': 'Kalé - Investigación', 'value': 'KINV'},
                            {'label': 'Kalé - Inyector', 'value': 'KINY'},
                            {'label': 'Platero - Investigación', 'value': 'PINV'},
                            {'label': 'Platero - Inyector', 'value': 'PINY'},
                            
                        ],
                        value='PINV',
                    ),
                html.H4("Fecha:", className="card-subtitle"),
                
                dcc.DatePickerSingle(
                            id='Fecha',
                            min_date_allowed=sismos['UTC'].min(),
                            max_date_allowed=sismos['UTC'].max(),
                            initial_visible_month=sismos['UTC'].max(),
                            date=date(sismos['UTC'].max().year,sismos['UTC'].max().month,sismos['UTC'].max().day)
                ),
                html.H4("Hora-Minuto-Segundo:", className="card-subtitle"),
                html.Div(
                    [
                        dcc.Input(
                            id="Hora",
                            type="number",
                            placeholder="Hora",
                            size='6',
                            min=0, max=23, step=1,
                            value=sismos['UTC'].max().hour
                        ),
                        dcc.Input(
                            id="Minuto",
                            type="number",
                            placeholder="Minuto",
                            size='10',
                            min=0, max=59, step=1,
                            value=sismos['UTC'].max().minute
                        ),
                        dcc.Input(
                            id="Segundo",
                            type="number",
                            placeholder="Segundo",
                            size='10',
                            min=0, max=59, step=1,
                            value=sismos['UTC'].max().second
                        ),

                    ]

                ),
                html.H6(f"Ultimo sismos registrado : {str(sismos['UTC'].max())}"),
                html.Button(id='button',
                children='Sismicidad acumulada mensual (30 días previos) ',
                n_clicks=0,
                style=white_button_style),  
                html.H4(id='Alert'),
                
                dash_table.DataTable(
                    id='Table',
                    style_header={
                                'backgroundColor': 'rgb(220, 220, 220)',
                                'fontWeight': 'bold',
                                'color': 'black',
                            },
                    style_data={
                        'color': 'black',
                        'backgroundColor': 'white'
                    },
                    style_data_conditional=[

        {
            'if': {
                'filter_query': '{{Semaforo}} = {}'.format('Verde'),
                'column_id': 'Semaforo'
            },
            'backgroundColor': 'green',
            'color': 'black'
        },
        {
            'if': {
                'filter_query': '{{Semaforo}} = {}'.format('Amarillo'),
                'column_id': 'Semaforo'
            },
            'backgroundColor': 'yellow',
            'color': 'black'
        },
        {
            'if': {
                'filter_query': '{{Semaforo}} = {}'.format('Naranja'),
                'column_id': 'Semaforo'
            },
            'backgroundColor': 'orange',
            'color': 'black'
        },
                {
            'if': {
                'filter_query': '{{Semaforo}} = {}'.format('Rojo'),
                'column_id': 'Semaforo'
            },
            'backgroundColor': 'red',
            'color': 'black'
        },
                    ],),
                    dbc.CardImg(src="assets\logos.png", bottom=True, alt='Logos_convenio_tripartito',)   
                    ]),
                color="secondary", 
                inverse=True) 

card_graph = dbc.Card(
        dcc.Graph(id='3d_model', figure={}), body=True,color="dark",
)     

card_explication=dbc.Card(
    dbc.CardBody([
        html.H2("¿Qué es el semáforo sísmico?", className="card-title"),
        html.H6("El semáforo sísmico es un mecanismo desarrollado por el Servicio Geológico Colombiano (SGC) para la toma de decisiones en el desarrollo de las operaciones de las Pruebas Piloto de Investigación Integral (PPII). Para el semáforo se han definido cuatro colores: verde, amarillo, naranja y rojo. Adicionalmente, se presenta enmarcado dentro de dos volúmenes cilíndricos denominados volúmen de monitoreo (correspondiente al cilíndro externo) y volúmen de suspensión (correspondiente al cilindro interno), definidos de acuerdo con la propuesta del semáforo sísmico (Dionicio et al., 2020). Los volumenes cilíndricos cuentan con una profundidad de 16 km,  radio interno de dos veces la profundidad medida del pozo (Dionicio et al., 2020) y externo de dos veces la profundidad medida del pozo más veinte kilómetros (2h + 20km), de acuerdo con la Resolución 40185 de 2020 del Ministerio de Minas y Energía.",
            className="card-text"),
        html.H6("La clasificación en colores del semáforo se realiza para cada uno de los diferentes rangos de magnitud de los eventos sísmicos que entren dentro de los volúmenes cilíndricos. Los rangos de magnitud son m0, m1, m2, m3 y m4, que tendrán diferentes estados del semáforo, son dependientes del número de sismos registrados diarios para cada uno de esos rangos, cuyos valores se comparan con los parámetros definidos en el documento propuesto para el semáforo sísmico, con el fin de obtener el correspondiente color del semáforo (Dionicio et al., 2020).", 
            className="card-text"),
        dbc.CardImg(src="assets\Tabla7a.png", bottom=True, alt='Tabla7a',),
        dbc.CardImg(src="assets\Tabla7b.png", bottom=True, alt='Tabla7b',),
        html.H6("Adicionalmente, a medida que se desarrolla el monitoreo diario de las actividades, se registra la acumulación de alertas para cada uno de los colores del semáforo sísmico, donde se asigna una puntuación para cada color de 0 para verde, 1 para amarillo y 3 para naranja (Dionicio et al., 2020). A partir de la puntuación acumulada mensual, se definen las acciones propuestas acordes con el esquema de puntuación del seguimiento mensual de sismicidad montoreada de los PPII (Dionicio et al., 2020).", 
            className="card-text"),
        dbc.CardImg(src="assets\Tabla8.png", bottom=True, alt='Tabla8',),
    ]))


card_references=dbc.Card(
    dbc.CardBody([
        html.H2("Referencias", className="card-title"),
        html.H6("Dionicio, V., Mercado Días, O., & Lizarazo Calderón, M. (2020). Semáforo para el monitoreo sísmico durante el desarrollo de los proyectos piloto de investigación integral en yacimientos no convencionales de hidrocarburos en Colombia.", 
            className="card-text"),
        html.H6("Global Multi-Resolution Topography (GMRT) Data Synthesis. Distributed by OpenTopography. https://doi.org/10.1029/2008GC002332 . Accessed: 2022-04-06", 
            className="card-text"),
        html.H6("Instituto Geográfico Agustin Codazzi - IGAC (2019). Base de datos vectorial básica. Colombia. Escala 1:100.000. Colombia en Mapas. https://www.colombiaenmapas.gov.co/#", 
            className="card-text"),
        html.H6("Ministerio de Minas y Energía (07 de julio de 2020). Resolución 40185 de 2020. Por la cual se establecen lineamientos técnicos para el desarrollo de los Proyecto Piloto de Investigación Integral - PPII en Yacimientos No Convencionales - YNC de Hidrocarburos a través de la técnica de Fracturamiento Hidráulico Multietapa con Perforación Horizontal - FH-PH.", 
            className="card-text"),
    ]))

app.layout = html.Div([
    dbc.Row([dbc.Col(card_main, width=4),
             dbc.Col(card_graph, width=8),
             dbc.Col(card_explication, width=12),
             dbc.Col(card_references, width=12)], 
             justify="center"),             
])

@app.callback(
     dash.dependencies.Output(component_id='3d_model', component_property='figure'),



    [dash.dependencies.Input(component_id='POZO', component_property='value'),
     dash.dependencies.Input(component_id='Fecha', component_property='date'),
     dash.dependencies.Input(component_id='Hora', component_property='value'),
     dash.dependencies.Input(component_id='Minuto', component_property='value'), 
     dash.dependencies.Input(component_id='Segundo', component_property='value'),
     dash.dependencies.Input('button', 'n_clicks')   ])

def update_output(pozo,Fecha,Hora,Minuto,Segundo,n_clicks):
        if pozo=='KINV':
            kale,nam,geo_inv,cyl1,bcircles1,cyl2,bcircles2,cyl3,bcircles3,sismos_local,ND,mn,nmsod_mn,npseod_mn,d_mn,x_pozo_inv_kale,y_pozo_inv_kale,r1,r_ext=kale2,nam2,geo_inv2,cyl12,bcircles12,cyl22,bcircles22,cyl32,bcircles32,sismos_local2,ND2,mn2,nmsod_mn2,npseod_mn2,d_mn2,x_pozo_inv_kale2,y_pozo_inv_kale2,r12,r_ext2
        elif pozo=='KINY':
            kale,nam,geo_inv,cyl1,bcircles1,cyl2,bcircles2,cyl3,bcircles3,sismos_local,ND,mn,nmsod_mn,npseod_mn,d_mn,x_pozo_inv_kale,y_pozo_inv_kale,r1,r_ext=kale1,nam1,geo_inv1,cyl11,bcircles11,cyl21,bcircles21,cyl31,bcircles31,sismos_local1,ND1,mn1,nmsod_mn1,npseod_mn1,d_mn1,x_pozo_inv_kale1,y_pozo_inv_kale1,r11,r_ext1
        elif pozo=='PINV':
            kale,nam,geo_inv,cyl1,bcircles1,cyl2,bcircles2,cyl3,bcircles3,sismos_local,ND,mn,nmsod_mn,npseod_mn,d_mn,x_pozo_inv_kale,y_pozo_inv_kale,r1,r_ext=kale4,nam4,geo_inv4,cyl14,bcircles14,cyl24,bcircles24,cyl34,bcircles34,sismos_local4,ND4,mn4,nmsod_mn4,npseod_mn4,d_mn4,x_pozo_inv_kale4,y_pozo_inv_kale4,r14,r_ext4
        else:
            kale,nam,geo_inv,cyl1,bcircles1,cyl2,bcircles2,cyl3,bcircles3,sismos_local,ND,mn,nmsod_mn,npseod_mn,d_mn,x_pozo_inv_kale,y_pozo_inv_kale,r1,r_ext=kale3,nam3,geo_inv3,cyl13,bcircles13,cyl23,bcircles23,cyl33,bcircles33,sismos_local3,ND3,mn3,nmsod_mn3,npseod_mn3,d_mn3,x_pozo_inv_kale3,y_pozo_inv_kale3,r13,r_ext3
        Hora=str(Hora)
        Minuto=str(Minuto)
        Segundo=str(Segundo)
        date=str(Fecha)+' '+Hora+':'+Minuto+':'+Segundo
        # df,col,sum,sismos_dia,sismos_mes=semaforo_sismico(sismos_local,Mc,ND,mn,
        #                 nmsod_mn,npseod_mn,d_mn,x_pozo_inv_kale,y_pozo_inv_kale,r1,r_ext,date)
        
        time=pd.to_datetime(date)
        sismos_dia_t = sismos[(sismos['UTC']<=time)&(sismos['UTC']>=time- timedelta(hours=24))]
        sismos_mes_t = sismos[(sismos['UTC']<=time)&(sismos['UTC']>=time- timedelta(days=30))]
        if n_clicks==0:
            pass
        elif n_clicks % 2!=0:
            sismos_dia_t=sismos_mes_t
        else:
            pass
        #Elaboramos la grafica con los datos siendo la variables anteriores
        layout = go.Layout(scene_xaxis_visible=True, scene_yaxis_visible=True, scene_zaxis_visible=True)
        fig = go.Figure(data=[cyl1, bcircles1,cyl2, bcircles2,cyl3, bcircles3, ], layout=layout)
        # for i in df_rivers['DRENAJE'].unique():
        #         riv=df_rivers[df_rivers['DRENAJE']==i]
        #         fig.add_trace(go.Scatter3d(z=riv['Z'], x=riv['X'], y=riv['Y'],mode='markers',
        #         name=str(i),marker_symbol='square',marker=dict(color='aqua',size=2)))
        for i in df_rivers['COD_UC'].unique():
                riv=df_rivers[df_rivers['COD_UC']==i]
                fig.add_trace(go.Scatter3d(z=riv['Z'], x=riv['X'], y=riv['Y'],mode='markers',
                name=str(i),marker_symbol='square',marker=dict(color='aqua',size=2)))
        if len(sismos_dia_t)>0:

                    sismos_1 = go.Scatter3d(
                        x = sismos_dia_t['LONGITUD (°)'],
                        y = sismos_dia_t['LATITUD (°)'],
                        z = sismos_dia_t['PROF. (Km)']*1000*-1,
                        mode='markers',
                        marker=dict(
                            size=(2*sismos_dia_t['MAGNITUD'])**2,
                            color=sismos_dia_t['PROF. (Km)']*1000,                # set color to an array/list of desired values
                            colorscale='Jet_r',   # choose a colorscale
                            opacity=1,
                            cmax=0,
                            cmin=32000,
                        ),
                        error_x=dict(
                            array=sismos_dia_t['ERROR LONGITUD (°)'],                # set color to an array/list of desired values
                            color='red',   # choose a colorscale
                            symmetric=True,
                            width=0.01
                        ),
                        error_y=dict(
                            array=sismos_dia_t['ERROR LATITUD (°)'],                # set color to an array/list of desired values
                            color='red',   # choose a colorscale
                            symmetric=True,
                            width=0.01
                        ),
                        error_z=dict(
                            array=sismos_dia_t['ERROR PROFUNDIDAD (Km)']*1000,                # set color to an array/list of desired values
                            color='red',   # choose a colorscale
                            symmetric=True,
                            width=0.01
                        ),
                        hovertemplate='Longitud: '+sismos_dia_t['LONGITUD (°)'].apply(lambda x:str(x))+'°'+'<br>'+
                                    'Latitud: '+sismos_dia_t['LATITUD (°)'].apply(lambda x:str(x))+'°'+'<br>'+
                                    'X:'+sismos_dia_t['ESTE'].apply(lambda x:str(x))+'<br>'+
                                    'Y:'+sismos_dia_t['NORTE'].apply(lambda x:str(x))+'<br>'+
                                    'Profundidad :'+(sismos_dia_t['PROF. (Km)']*1000).apply(lambda x:str(x))+'m <br>'+
                                    'Fecha :'+sismos_dia_t['FECHA - HORA UTC'].apply(lambda x:str(x))+'<br>'+
                                    'Magnitud:'+sismos_dia_t['MAGNITUD'].apply(lambda x:str(x))+'<br>'+
                                    'Tipo de magnitud:'+sismos_dia_t['TIPO MAGNITUD']+'<br>'+
                                    #'Fases:'+sismos_dia['FASES'].apply(lambda x:str(x))+'<br>'+
                                    'RMS (Segundos):'+sismos_dia_t['RMS (Seg)'].apply(lambda x:str(x))+'s <br>'+
                                    'Error en la latitud (m):'+sismos_dia_t['ERROR LATITUD (Km)'].apply(lambda x:str(x*1000))+'m <br>'+
                                    'Error en la longitud (m):'+sismos_dia_t['ERROR LONGITUD (Km)'].apply(lambda x:str(x*1000))+'m <br>'+
                                    'Error en la profundidad (m):'+sismos_dia_t['ERROR PROFUNDIDAD (Km)'].apply(lambda x:str(x*1000)),#+'m <br>'+
                                    #'Región:'+sismos_dia['REGION']+'<br>'+
                                    #'Estado:'+sismos_dia['ESTADO'],
                            name='Sismos',
                            showlegend=False)  
                    fig.add_trace(sismos_1)
        fig.add_trace(go.Surface(z=z_topo,showscale=False, x=x_topo, y=y_topo,colorscale=['green','greenyellow','saddlebrown','saddlebrown','saddlebrown','saddlebrown','snow','snow'],
                            showlegend=False,opacity=0.8,name='Topografía',hoverinfo='skip'))
        fig.add_trace(kale)
        fig.update_layout(autosize=False,
                        width=850, height=725,
                        margin=dict(l=50, r=50, b=50, t=50),)
        fig.add_trace(Poblaciones)

        fig.update_layout(
                scene=dict(
                annotations=[dict(
            showarrow=False,
            x=geo_inv[1],
            y=geo_inv[0],
            z=310,
            text=nam,
            xanchor="left",
            xshift=10,
            opacity=0.7,
            font=dict(
                color="black",
                size=12
            ))]))
        fig.update_layout(
        scene = dict(aspectratio=dict(x=52,y=52,z=38),
                xaxis = dict(title='X',nticks=10, range=[gw,ge]),
                yaxis = dict(title='Y',nticks=10, range=[gs,gn],),
                zaxis = dict(title='Elevación(msnm)',nticks=10, range=[-32000,6000],),),)
        fig.update_traces(showlegend=False)
        fig.update_layout(
            scene=dict(
            annotations=Pobl))
        return fig

@app.callback([dash.dependencies.Output('Table','data'),
                dash.dependencies.Output('Table','columns'),
                dash.dependencies.Output(component_id='SEM', component_property='src'),
                dash.dependencies.Output(component_id='Alert', component_property='children'),],
                [dash.dependencies.Input(component_id='POZO', component_property='value'),
                dash.dependencies.Input(component_id='Fecha', component_property='date'),
                dash.dependencies.Input(component_id='Hora', component_property='value'),
                dash.dependencies.Input(component_id='Minuto', component_property='value'), 
                dash.dependencies.Input(component_id='Segundo', component_property='value'),   ],)

def update_datatable(pozo,Fecha,Hora,Minuto,Segundo):
    if pozo == 'KINV':
        kale, nam, geo_inv, cyl1, bcircles1, cyl2, bcircles2, cyl3, bcircles3, sismos_local, ND, mn, nmsod_mn, npseod_mn, d_mn, x_pozo_inv_kale, y_pozo_inv_kale, r1, r_ext = kale2, nam2, geo_inv2, cyl12, bcircles12, cyl22, bcircles22, cyl32, bcircles32, sismos_local2, ND2, mn2, nmsod_mn2, npseod_mn2, d_mn2, x_pozo_inv_kale2, y_pozo_inv_kale2, r12, r_ext2
    elif pozo == 'KINY':
        kale, nam, geo_inv, cyl1, bcircles1, cyl2, bcircles2, cyl3, bcircles3, sismos_local, ND, mn, nmsod_mn, npseod_mn, d_mn, x_pozo_inv_kale, y_pozo_inv_kale, r1, r_ext = kale1, nam1, geo_inv1, cyl11, bcircles11, cyl21, bcircles21, cyl31, bcircles31, sismos_local1, ND1, mn1, nmsod_mn1, npseod_mn1, d_mn1, x_pozo_inv_kale1, y_pozo_inv_kale1, r11, r_ext1
    elif pozo == 'PINV':
        kale, nam, geo_inv, cyl1, bcircles1, cyl2, bcircles2, cyl3, bcircles3, sismos_local, ND, mn, nmsod_mn, npseod_mn, d_mn, x_pozo_inv_kale, y_pozo_inv_kale, r1, r_ext = kale4, nam4, geo_inv4, cyl14, bcircles14, cyl24, bcircles24, cyl34, bcircles34, sismos_local4, ND4, mn4, nmsod_mn4, npseod_mn4, d_mn4, x_pozo_inv_kale4, y_pozo_inv_kale4, r14, r_ext4
    else:
        kale, nam, geo_inv, cyl1, bcircles1, cyl2, bcircles2, cyl3, bcircles3, sismos_local, ND, mn, nmsod_mn, npseod_mn, d_mn, x_pozo_inv_kale, y_pozo_inv_kale, r1, r_ext = kale3, nam3, geo_inv3, cyl13, bcircles13, cyl23, bcircles23, cyl33, bcircles33, sismos_local3, ND3, mn3, nmsod_mn3, npseod_mn3, d_mn3, x_pozo_inv_kale3, y_pozo_inv_kale3, r13, r_ext3
    Hora=str(Hora)
    Minuto=str(Minuto)
    Segundo=str(Segundo)
    date=str(Fecha)+' '+Hora+':'+Minuto+':'+Segundo
    df,col,sum,sismos_dia,_=semaforo_sismico(sismos_local,Mc,ND,mn,nmsod_mn,npseod_mn,d_mn,x_pozo_inv_kale,y_pozo_inv_kale,r1,r_ext,date)            
    return df.to_dict('records'),[{"name": i, "id": i} for i in df.columns],f"assets\{col}.png",f"Alertas acumuladas: {sum}"

#Cambiar color del boton
@app.callback(dash.dependencies.Output('button', 'style'), [dash.dependencies.Input('button', 'n_clicks')])
def change_button_style(n_clicks):
    if n_clicks==0:
        return white_button_style
    elif n_clicks % 2!=0:
        return red_button_style
    else:
        return white_button_style

if __name__ == "__main__":
    app.run_server(debug=True)