# SIGATA — Sistema Integral para la Gestión y Trazabilidad de las Acciones Afirmativas

Aplicación web desarrollada en **Python + Streamlit** para administrar de forma integral la información de las acciones afirmativas dirigidas a la población recicladora de oficio, en el marco del proyecto de investigación:

> *"Diseño de una propuesta de estrategia de innovación para fortalecer la gestión de las acciones afirmativas dirigidas a la población recicladora de oficio en la Subdirección de Aprovechamiento de la UAESP, en el marco del ODS 12: Producción y Consumo Responsables."*

Este proyecto constituye el **Producto Mínimo Viable (MVP)** de dicha estrategia de innovación.

## Funcionalidades

- **Dashboard Ejecutivo** con tarjetas KPI, visualizaciones interactivas, análisis ejecutivo automático en lenguaje natural y recomendaciones que se actualizan según los filtros aplicados.
- **Carga de Excel** con detección automática de hojas, columnas, tipos de dato y cantidad de registros.
- **Configuración / mapeo automático de columnas**, para que archivos con distinta estructura se integren sin modificar código.
- **Registro (CRUD)** de acciones afirmativas, recicladores, organizaciones (ORO), programas, proyectos, responsables, incentivos y líneas de acción.
- **Gestión documental**: carga de PDF, imágenes y soportes asociados a cada acción afirmativa.
- **Mapa de Bogotá** (Folium) con organizaciones, recicladores, cobertura territorial y mapa de calor de concentración de beneficios.
- **Filtros inteligentes** (año, mes, localidad, organización, programa, proyecto, responsable, estado, sexo, grupo poblacional, tipo de acción) que actualizan toda la aplicación.
- **Ficha 360°** del reciclador: datos personales, historial, beneficios, documentos y línea de tiempo.
- **Alertas inteligentes**: acciones vencidas, beneficiarios duplicados, documentos faltantes, información incompleta, organizaciones sin seguimiento, presupuestos agotados y acciones pendientes.
- **Reportes automáticos** en PDF, Excel y Word, respetando los filtros aplicados.
- **Datos de demostración realistas** generados automáticamente la primera vez que se ejecuta la aplicación (sin Lorem Ipsum).

## Estructura del proyecto

```
SIGATA/
├── app.py                     # Punto de entrada — Dashboard Ejecutivo (Inicio)
├── requirements.txt
├── .streamlit/config.toml     # Tema visual institucional
├── config/
│   └── settings.py            # Constantes, colores, catálogos, localidades
├── modules/
│   ├── database.py            # Acceso a datos (SQLite)
│   ├── demo_data_generator.py # Generador de datos demo realistas
│   ├── data_loader.py         # Carga y perfilado de archivos Excel
│   ├── column_mapper.py       # Mapeo automático de columnas
│   ├── kpis.py                # Cálculo de indicadores
│   ├── charts.py              # Fábrica de visualizaciones Plotly
│   ├── analisis.py            # Análisis ejecutivo (NLG) y recomendaciones
│   ├── filtros.py             # Filtros inteligentes reutilizables
│   ├── forms.py               # CRUD genérico de registro
│   ├── documentos.py          # Gestión documental
│   ├── mapa.py                # Mapa de Bogotá (Folium)
│   ├── ficha360.py             # Ficha 360° del reciclador
│   ├── alertas.py             # Motor de alertas inteligentes
│   ├── reportes.py            # Generación de reportes PDF / Excel / Word
│   └── ui.py                  # Estilos y componentes visuales (KPI cards, etc.)
├── pages/
│   ├── 1_📥_Carga_de_Datos.py
│   ├── 2_⚙️_Configuracion_Mapeo.py
│   ├── 3_📝_Registro.py
│   ├── 4_📁_Gestion_Documental.py
│   ├── 5_🗺️_Mapa.py
│   ├── 6_👤_Ficha_360.py
│   ├── 7_🔔_Alertas.py
│   └── 8_📄_Reportes.py
└── data/
    ├── sigata.db               # Base de datos SQLite (se crea automáticamente)
    └── documents/               # Soportes documentales cargados
```

## Instalación y ejecución (Visual Studio Code)

1. Abra la carpeta `SIGATA` en Visual Studio Code.
2. Cree y active un entorno virtual (recomendado):

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. Instale las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Ejecute la aplicación:

   ```bash
   streamlit run app.py
   ```

5. Abra el navegador en la URL indicada por Streamlit (por defecto `http://localhost:8501`).

La primera vez que se ejecuta, SIGATA crea automáticamente la base de datos SQLite (`data/sigata.db`) y la puebla con un conjunto de datos demo realistas (organizaciones, recicladores y acciones afirmativas de los últimos tres años), de modo que todas las funcionalidades sean explorables de inmediato. Para trabajar con información real, use la página **"Carga de Datos"** y luego **"Configuración Mapeo"**.

## Notas técnicas

- Motor de datos: **SQLite** embebido (sin necesidad de servidor de base de datos).
- El mapa usa coordenadas de centroide por localidad (no direcciones exactas), con dispersión determinística para representar concentración territorial.
- El análisis ejecutivo y las recomendaciones se generan con reglas deterministas sobre los propios datos (sin dependencias externas ni conexión a internet).
- Para reiniciar el sistema con datos limpios, elimine el archivo `data/sigata.db` y la carpeta `data/documents/`, y vuelva a ejecutar la aplicación.
