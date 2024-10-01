# Análisis de Datos de Siniestros

Este proyecto realiza un análisis de datos de siniestros utilizando archivos de Excel. A través de este análisis, se pueden obtener métricas como la siniestralidad mensual, las coberturas con mayor y menor cantidad de siniestros, y la severidad promedio por rango etario, entre otros.

## Requerimientos

Para ejecutar el código, necesitarás tener instalados los siguientes paquetes de Python:

- `pandas`
- `openpyxl` (para leer archivos Excel)
- `datetime`

Puedes instalarlos utilizando pip ejemplo:

```bash
pip install pandas openpyxl
```

## Estructura del Código

1. **Carga de Datos**: 
   - El script carga los archivos de Excel desde una ruta específica y almacena los datos en DataFrames de Pandas.

2. **Filtrado de Datos**:
   - Se filtran los servicios donde el monto es diferente de cero y se seleccionan columnas relevantes de cada DataFrame.

3. **Unión de Tablas**:
   - Se realizan múltiples uniones (merges) entre los DataFrames para crear un conjunto de datos completo.

4. **Análisis**:
   - Se calculan la severidad de los gastos, la siniestralidad mensual, la cantidad de siniestros por cobertura, y se evalúa la siniestralidad por partner.

5. **Análisis de Edad**:
   - Se determina el rango etario de los usuarios siniestrados y se calcula su severidad promedio.

## Cómo Ejecutar el Código

1. **Cambia la Ruta de los Archivos**:
   - Asegúrate de cambiar la variable `ruta` en el script a la ubicación de tus archivos Excel en tu sistema:
   ```python
   ruta = r'C:\Users\JEAN\Documents\Crabi\data analysis'
   ```

2. **Ejecuta el Script**:
   - Puedes ejecutar el script en tu entorno de desarrollo de Python preferido. Asegúrate de que todos los archivos de Excel necesarios estén en la ruta especificada.

3. **Resultados**:
   - El script imprimirá varias salidas en la consola, incluyendo la siniestralidad mensual, las coberturas con mayor y menor cantidad de siniestros, y la severidad promedio por rango etario.

## Notas Adicionales

- El análisis se basa en supuestos y parámetros establecidos en el código. Se debe revisar y ajustarlo según sea necesario.
- Cualquier error encontrado al leer archivos será informado en la consola.

## Contribuciones

Si deseas contribuir a este proyecto, siéntete libre de hacer un fork y enviar pull requests con mejoras o correcciones.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
