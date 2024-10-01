import os
import pandas as pd
from datetime import datetime


#Ruta a los archivos
ruta = r'C:\Users\JEAN\Documents\Crabi\data analysis'

# Lista para almacenar
dataframes = []
nombres_archivos = [] 

#Fragmento de código para recorrer la ruta y leer los archivos 
for archivo in os.listdir(ruta):
    if archivo.endswith('.xlsx'):  
        ruta_completa = os.path.join(ruta, archivo)
        print(f"Leyendo archivo: {archivo}")
        try:
            df = pd.read_excel(ruta_completa)
            dataframes.append(df)
            nombres_archivos.append(archivo)
        except Exception as e:
            print(f"Error en el archivo: {archivo}: {e}")

# Imprimir los nombres de los archivos e indice (para poder usar de referencia al asignar variable)
if nombres_archivos:
    for idx, nombre in enumerate(nombres_archivos):
        print(f"{idx}: {nombre}")
else:
    print("No se encontraron archivos.")



#Asignación del dataframe
claim = dataframes[0]
people = dataframes[2]
service = dataframes[3]
status = dataframes[4]
status_cause = dataframes[5]
status_type = dataframes[6]



#Referencial para ver todas las columnas
pd.set_option('display.max_columns', None)



#filtrar los servicios con amount diferente de 0, acorde al requerimiento. 
service_filtered = service.fillna(0)
service_filtered = service_filtered[(service_filtered['amount'] != 0)]



#Selección de columnas
columns_claims = ["id", "type_status_id", "address_id", "original_claim_id", "liability_status_id", "cancelled_reason_status_id",
                  "status_cause_type_id", "policy_number", "occurred_at", "created_at", "updated_at"]

columns_people = ["id", "claim_id", "type_status_id", "vehicle_id", "license_id", "policy_id", "address_id","created_at", "updated_at",'birthdate']

columns_services = ["id", "type_status_id", "people_id", "provider_id", "subprovider_id", "coverage_id", "amount", "deductible","created_at",
                    "updated_at"]

columns_status = ['id',	'status_type_id','name','description']




#Union de tablas 
claim_comb = pd.merge(claim[columns_claims], people[columns_people], left_on = 'id', right_on = 'claim_id', how = 'inner')
claim_comb = pd.merge(claim_comb, service_filtered[columns_services], left_on = 'id_y', right_on = 'people_id', how = 'inner')
claim_comb = claim_comb.drop(columns = 'id')
claim_comb = pd.merge(claim_comb, status[columns_status], left_on='type_status_id', right_on='id', how='inner')
claim_comb = claim_comb.drop(columns = 'id')




claim_comb



# Convertir la columna a tipo datetime
claim_comb['created_at_x'] = pd.to_datetime(claim_comb['created_at_x'])

# Extraer fecha
claim_comb['claim_created_date'] = claim_comb['created_at_x'].dt.date

# Extraer el mes 
claim_comb['month'] = claim_comb['created_at_x'].dt.month
claim_comb = claim_comb.copy()

#filtro solo gastos
claim_comb = claim_comb [claim_comb ['amount'] < 0]



#Calculo deductible relativo, acorde al requerimiento de la primera pregunta

def calcular_deductible_relativo(row):
    if row['coverage_id'] == 0 or row['name'] == '*No Aplica':
        return False
    else:
        return row['deductible'] 

claim_comb['deductible_relativo'] = claim_comb.apply(calcular_deductible_relativo, axis=1)


#Agrupación de suma agregada para obtener las combinanciones de gastos que se le aplica deductible
gastos_agrupados_parcial = claim_comb.groupby(['claim_id','deductible_relativo']).agg({
    'amount': 'sum',
}).reset_index()

#Severidad
##En este caso se tiene el supuesto de que si hay deductible y este es mayor al gasto, retorna 0 ya que cubre el gasto (Esto puede cambiar segun el requerimiento).
def calcular_severidad(row):
    if row['deductible_relativo'] == True:  
        deductible = 0.05 * 100000  # 5% de 100k
        return row['amount'] + deductible if abs(row['amount']) > deductible else 0  
    return row['amount']

gastos_agrupados_parcial['severidad'] = gastos_agrupados_parcial.apply(calcular_severidad, axis=1)



#Suma agrupada una vez, los deducibles fueron aplicados
gastos_agrupados = gastos_agrupados_parcial.groupby('claim_id').agg({
    'severidad': 'sum',
}).reset_index()

claim_comb_unique = claim_comb.groupby(['claim_id']).agg({
    'month': 'first',  # O la función que consideres adecuada, como 'max' o 'min'
}).reset_index()

gastos_agrupados = pd.merge(gastos_agrupados, claim_comb_unique[['claim_id', 'month']], on = 'claim_id', how = 'left')



gastos_mensuales = gastos_agrupados.groupby('month').agg({
    'severidad': 'sum',  # Sumar los gastos
}).reset_index()



# 200k de primas devengada, acorde al ejercicio
gastos_mensuales['siniestralidad'] = gastos_mensuales['severidad'] / 200000
print('\n ¿Cuál es la siniestralidad mensual de la compañía?\n')
print(gastos_mensuales)


#¿Cuál es la cobertura con mayor y menor cantidad de siniestros?



print('\n¿Cuál es la cobertura con mayor y menor cantidad de siniestros?')

unique_coverage = claim_comb[['claim_id', 'coverage_id']].drop_duplicates()
coverage_count = unique_coverage.groupby('coverage_id').size().reset_index(name='count')
coverage_count = coverage_count[coverage_count['coverage_id'] != 0]
coverage_count = coverage_count.sort_values(by = 'count', ascending = False)
print(coverage_count)



max_row = coverage_count.loc[coverage_count['count'].idxmax()]
min_row = coverage_count.loc[coverage_count['count'].idxmin()]

print("\nLa cobertura con mayor cantidad de siniestros:")
print(f"Coverage ID: {max_row['coverage_id']}, Count: {max_row['count']}")

print("\nLa cobertura con menor cantidad de siniestros:")
print(f"Coverage ID: {min_row['coverage_id']}, Count: {min_row['count']}")



#¿Cuál es el partner con mayor y menor siniestralidad? ¿cuál es su severidad promedio?

# Extraer las dos primeras letras de policy_number
claim_comb['partner'] = claim_comb['policy_number'].str[:2]

#Se agrupa por el claim para traer su partner
partner_unique = claim_comb.groupby(['claim_id']).agg({
    'partner': 'first',
}).reset_index()

#Agrupación de suma agregada para obtener las combinanciones de gastos que se le aplica deducible
gastos_partner = claim_comb.groupby(['claim_id','deductible']).agg({
    'amount': 'sum',  
}).reset_index()

def calcular_severidad2(row):
    if row['deductible'] == True:  
        deductible = 0.05 * 100000  # 5% de 100k
        return row['amount'] + deductible if abs(row['amount']) > deductible else 0
    return row['amount']

gastos_partner['severidad'] = gastos_partner.apply(calcular_severidad2, axis=1)

gastos_partner = gastos_partner.groupby('claim_id').agg({
    'severidad': 'sum',
}).reset_index()

partner_group = pd.merge(gastos_partner, partner_unique, on = 'claim_id', how = 'left')

partner_group_avg = partner_group.groupby('partner').agg({
    'severidad': 'mean', 
}).reset_index()



print('\n\n¿Cuál es el partner con mayor y menor siniestralidad? ¿cuál es su severidad promedio?')
print("\n Severidad promedio por partner:")
print(partner_group_avg)



partner_group_sum = partner_group.groupby('partner').agg({
    'severidad': 'sum',
}).reset_index()

partner_group_sum['siniestralidad'] = partner_group_sum['severidad'] / 1200000  # Asumimos 200k de primas devengadas

partner_group_sum = partner_group_sum.sort_values(by = 'siniestralidad', ascending = False)




print('\n')
print(partner_group_sum)

max_row = partner_group_sum.loc[partner_group_sum['siniestralidad'].idxmax()]
min_row = partner_group_sum.loc[partner_group_sum['siniestralidad'].idxmin()]

print("\nLa mayor siniestralidad es:")
print(f"El partner: {min_row['partner']}, con siniestralidad: {min_row['siniestralidad']}")

print("\nLa mayor siniestralidad es::")
print(f"El partner : {max_row['partner']}, con siniestralidad: {max_row['siniestralidad']}")




#Utilizando los datos de la tabla people , ¿dentro de qué rango etario se
#encuentra la mayor y menor cantidad de usuarios siniestrados? ¿cuál es su
#severidad promedio?


claim_comb['birthdate'] = pd.to_datetime(claim_comb['birthdate'])

# Calcular la edad
today = pd.to_datetime(datetime.now().date())  # Obtener la fecha actual
claim_comb['age'] = (today - claim_comb['birthdate']).dt.days // 365  # Calcular la edad en años

#Parametros para categorizar
bins = [0, 18, 35, 50, 100]
labels = ['0-18', '19-35', '36-50', '51+']

#crear el nuevo campo ya categorizado
claim_comb['age_group'] = pd.cut(claim_comb['age'], bins=bins, labels=labels, right=False)


unique_age_group= claim_comb[['claim_id', 'age_group']].drop_duplicates()
age_count = unique_age_group.groupby('age_group', observed = False).size().reset_index(name='count')
age_count = age_count.sort_values(by = 'count', ascending = False)



age_sever = claim_comb.groupby(['claim_id','deductible','age_group'], observed = True).agg({
    'amount': 'sum',
}).reset_index()

age_sever['severidad'] = age_sever.apply(calcular_severidad2, axis=1)

age_sever = age_sever[age_sever['severidad'] != 0]

age_sever_avg = age_sever.groupby('age_group', observed = True).agg({
    'severidad': 'mean', 
}).reset_index()



print("\n\nUtilizando los datos de la tabla people, ¿dentro de qué rango etario se")
print("encuentra la mayor y menor cantidad de usuarios siniestrados? ¿cuál es su")
print("severidad promedio?\n")

max_row = age_count.loc[age_count['count'].idxmax()]
min_row = age_count.loc[age_count['count'].idxmin()]

print(age_count)

print("\nEl rango etario con mayor cantidad de siniestros es:")
print(f"el rango etario : {max_row['age_group']}, con: {max_row['count']}")

print("\nEl rango etario con menor cantidad de siniestros es")
print(f"el rango etario : {min_row['age_group']}, con siniestralidad: {min_row['count']}")

print(f"\n{age_sever_avg}")

middle_rows1 = age_sever_avg.iloc[1:2]
middle_rows2 = age_sever_avg.iloc[2:3]

print(f"\nEl rango etario: {middle_rows1['age_group'].iloc[0]}, tiene una severidad promedio de: {middle_rows1['severidad'].iloc[0]:.2f}")
print(f"\nEl rango etario: {middle_rows2['age_group'].iloc[0]}, tiene una severidad promedio de: {middle_rows2['severidad'].iloc[0]:.2f}")
