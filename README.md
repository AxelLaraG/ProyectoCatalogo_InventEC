# Funcionamiento básico

Cada compañero ya cuenta con su carpeta y rama creada, las ramas tienen sus respectivos nombres
mientras que las carpetas en las que trabajarán serán las de su respectivo módulo seleccionado o
asignado.

# Base de datos
La base de datos ya está creada, se trabajará en MongoDB bajo un cluster en **MongoDB Atlas**

## Datos de conexión
- La **cadena de conexión al clúster** la encuentran en el mensaje fijado del grupo de **whatsapp**
- El **nombre de la base de datos** es **proyecto**
- El **nombre de las colecciones** son: **equipos**,**prestamos** y **usuarios** si requieren crear alguna pueden hacerlo sin problema

Cualquier cambio que hagan a la base de datos es importante que **la comuniquen** en el grupo de whatsapp y que 
la **documenten** en este **readme.md**.

## Estructura de los documentos en Mongo
Hasta este momento, solo he definido la estructura de los **equipos** debido a que la requería para el _Módulo 1_
la estructura sigue la solicitada en el archivo de la profesora:

´´´

"_id": {
    "$oid": "682980755eb98bb052c83b12"
  },
  "nombre": "Proyector Epson X41",
  "modelo": "X41",
  "numero_serie": "EP123456789",
  "estado": "Disponible",
  "ubicacion": "Sala 1 - Estante A",
  "fecha_registro": {
    "$date": "2024-05-01T10:00:00Z"
  }

´´´
## Visualización de los datos
Les recomiendo utilizar **MongoDB Compass** y visualizar bien la estructura creada hasta el momento, también existe una extensión 
para **VSCode** llamada **MongoDB** en la cual solo colocan la cadena de conexión y podrán visualizar la información.

Cualquier duda pueden hacerla en el grupo c:
