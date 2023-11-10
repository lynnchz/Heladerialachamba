import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import csv
import time
from datetime import datetime
import datetime as dt
import webbrowser


def datos_boleta(db_file): #funcion que busca los datos del cliente
    resultados = {} #almacena la informacion sobre los clientes 
    
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    
    # Consulta SQL q obtiene los datos de clientes, productos, nombres de productos y precios
    cursor.execute("""
        SELECT c.NOMBRE, c.EMAIL, c.DOMIENTREGA, p.ncli, pr.PRODU, p.cant, pr.IMPORTE
        FROM Pedidos p
        JOIN Clientes c ON p.ncli = c.ncli
        JOIN Productos pr ON p.npro = pr.npro
    """)
    
    for x in cursor.fetchall():
        nombre_cliente, email, domicilio_entrega, ncli, nombre_producto, cant, precio_unitario = x

        # combierte ncli en str
        ncli = str(ncli)
        
        if ncli not in resultados: #verifica si el cliente esta en el diccionario
            resultados[ncli] = {
                "nombre_cliente": nombre_cliente,
                "email": email,
                "domicilio_entrega": domicilio_entrega,
                "productos": []
            }

        resultados[ncli]["productos"].append((nombre_producto, cant, precio_unitario)) #construye la estrucutra de datos que organiza la informacion para cada cliente en el diccionario resultados

    connection.close()
    return resultados

def generar_comprobantes(clientes_productos):
    # #estructura en HTML
    comprobante_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Comprobantes de Pago</title>
        <style>
            body {
                background-color: #010101;
                color: white;
                text-align: center;
            }
            table {
                width: 75%;
                margin: auto;
                border-collapse: collapse;
                border: 1px solid white;
            }
            th, td {
                border: 1px solid white;
                padding: 8px;
            }
            th {
                background-color: #1DA200;
                color: white;
            }
            h1 {
                color: #1DA200;
            }
            .recuadro {
                border: 2px solid #1DA200;
                padding: 10px;
                margin: 10px;
                border-radius: 10px;
            }
            button {
                background-color: #1DA200;
                color: white;
                padding: 10px;
                font-size: 16px;
                border: none;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h1>Comprobantes de Pago</h1>
    """

    comprobante_html += f"<p>Fecha del Comprobante: {dt.datetime.now().strftime('%Y-%m-%d')}</p>" #pone la fecha del dia


    for ncli, cliente_info in clientes_productos.items(): #itinera sobre los clientes en el diccionario
        total_cliente = 0  # Inicializa el total del cliente a 0 para saber cuanto $$ el cliente

        comprobante_html += f'<div class="recuadro"><h2>Cliente: {cliente_info["nombre_cliente"]}</h2>' #estrucutra de cada cliente 
        comprobante_html += f"<p>Email: {cliente_info['email']}</p>"
        comprobante_html += f"<p>Domicilio de entrega: {cliente_info['domicilio_entrega']}</p>"
        comprobante_html += "<table>"
        comprobante_html += "<tr><th>Pedido</th><th>Precio del Pedido</th><th>Total</th></tr>"

        for nombre_producto, cant, precio_unitario in cliente_info["productos"]: #itinera a travez de la lista productos para el cliente actual
            # Calcula el subtotal para cada producto y suma al total del cliente
            subtotal = cant * precio_unitario
            total_cliente += subtotal

            comprobante_html += f"<tr><td>{nombre_producto} - {cant} unidades</td><td>${precio_unitario}</td><td>${subtotal}</td></tr>" #agrega una fila a la tabla con detalles de lproducto

        comprobante_html += "</table>"
        comprobante_html += f"<p>Total a pagar: ${total_cliente}</p></div>" #Se cierra la tabla y se muestra el monto total que el cliente debe pagar


    # Botón imprimir
    comprobante_html += '<button onclick="window.print()">Imprimir</button>'

    comprobante_html += """
    </body>
    </html>
    """

    # Guarda el comprobante en un HTML
    with open("comprobantes.html", "w") as file:
        file.write(comprobante_html)

def agregar_cliente():
    # toma los datos
    nombre = nombre_cliente.get()
    direccion = direccion_cliente.get()
    telefono = telefono_cliente.get()
    email = email_cliente.get()
    localidad = localidad_cliente.get()
    domientrega = domientrega_cliente.get()
    id_zonas = id_zonas_var.get()
    id_vendedor = id_vendedor_cliente.get()
    cuit = cuit_cliente.get()
    deuda = deuda_cliente.get()

    # Validar que se hayan ingresado todos los datos solicitados
    if not nombre or not direccion or not telefono:
        messagebox.showerror("Error", "Por favor, complete todos los campos obligatorios.")
        return

    connection = sqlite3.connect('logistica.db')
    cur = connection.cursor()

    try:
        # carga los datos en la tabla Clientes
        cur.execute("INSERT INTO Clientes (NOMBRE, DOMIFISCAL, TELEFONO, EMAIL, LOCALIDAD, DOMIENTREGA, IDZonas, IDVendedor, CUIT, DEUDA) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (nombre, direccion, telefono, email, localidad, domientrega, id_zonas, id_vendedor, cuit, deuda))
        connection.commit()

        # Mostrar un mensaje de éxito
        messagebox.showinfo("Éxito", "El cliente se agregó correctamente.")
    except sqlite3.Error as e: #se ejecuta si hay alguna exepcion
        # En caso de error, mostrar un mensaje de error
        messagebox.showerror("Error", f"No se pudo agregar el cliente. Error: {str(e)}")
    finally: #se ejucta siempre
        # Cerrar la conexión a la base de datos
        connection.close()

    # Limpia los campos
    nombre_cliente.delete(0, tk.END)
    direccion_cliente.delete(0, tk.END)
    telefono_cliente.delete(0, tk.END)
    email_cliente.delete(0, tk.END)
    localidad_cliente.delete(0, tk.END)
    domientrega_cliente.delete(0, tk.END)
    id_zonas_var.delete(0, tk.END)
    id_vendedor_cliente.delete(0, tk.END)
    cuit_cliente.delete(0, tk.END)
    deuda_cliente.delete(0, tk.END)

def agregar_producto():
    # toma los datos ingresados por el usuario
    nombre_producto = nombre_producto_entry.get()
    descripcion_producto = descripcion_producto_entry.get()
    precio_producto = precio_producto_entry.get()
    stock_producto = stock_producto_entry.get()
    id_proveedor = id_proveedor_entry.get()

    # valida que se hayan ingresado todos los datos requeridos
    if not nombre_producto or not descripcion_producto or not precio_producto or not stock_producto or not id_proveedor:
        messagebox.showerror("Error", "Por favor, complete todos los campos obligatorios.")
        return

    connection = sqlite3.connect('logistica.db')
    cur = connection.cursor()

    try:
        # carga los datos en la tabla Productos
        cur.execute("INSERT INTO Productos (PRODU, IMPORTE, STOCK, IDProveedor) VALUES (?, ?, ?, ?)",
                    (nombre_producto, precio_producto, stock_producto, id_proveedor))
        connection.commit()

        #mensaje de éxito
        messagebox.showinfo("Éxito", "El producto se agregó correctamente.")
    except sqlite3.Error as e:
        # En caso de error, mostrar un mensaje
        messagebox.showerror("Error", f"No se pudo agregar el producto. Error: {str(e)}")
    finally:
        connection.close()

    # Limpia los campos
    nombre_producto_entry.delete(0, tk.END)
    descripcion_producto_entry.delete(0, tk.END)
    precio_producto_entry.delete(0, tk.END)
    stock_producto_entry.delete(0, tk.END)
    id_proveedor_entry.delete(0, tk.END)

def actualizar_db():
    conn = sqlite3.connect('logistica.db')
    cursor = conn.cursor()

    nuevo_nombre = "Nuevo Nombre"
    cliente_id = 1
    consulta_sql = f"UPDATE clientes SET nombre = ? WHERE id = ?"
    cursor.execute(consulta_sql, (nuevo_nombre, cliente_id))
    conn.commit()
    cursor.close()
    conn.close()
    print("Base de datos actualizada correctamente")

def leer_csv():#prueba
                # Abre el archivo CSV en modo lectura
    with open('C:/Users/Usuario/Desktop/Final programacion/FinalConMati/pedidos.csv', 'r') as archivo_csv:
                # Crea un objeto CSV para leer el archivo
        lector_csv = csv.reader(archivo_csv, delimiter=';')
                # Itera a través de las filas del archivo
    for reg in lector_csv:
                # Cada fila es una lista de valores
                # Accede a los valores por índice
        print(reg[0]+" * "+reg[1]+" * "+reg[2])

def restar_stock_producto(npro, cantidad):
    connection = sqlite3.connect("logistica.db")
    cur = connection.cursor()

    # Restar la cantidad de productos del stock en la tabla Productos
    cur.execute("UPDATE Productos SET STOCK = STOCK - ? WHERE npro = ?", (cantidad, npro))
    connection.commit()
    connection.close()

def agregar_pedidos():
    connection = sqlite3.connect('logistica.db')
    cur = connection.cursor()

    # Abre el archivo CSV de pedidos
    with open("pedidos.csv", "r") as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Saltar la primera línea (encabezados)

        restart = 0
        for line in file:
            # Dividir la línea del archivo CSV en sus campos (asumiendo tres campos en el archivo)
            fields = line.strip().split(";")

            if len(fields) == 3:  #valida que la longitud sea igual a 3
                ncli, cant, npro = fields
                #print(f"ncli: {ncli}, cant: {cant}, npro: {npro}")

                # Insertar los campos en la tabla Pedidos
                cur.execute("INSERT INTO Pedidos (ncli, cant, npro) VALUES (?, ?, ?)", (ncli, cant, npro))
                connection.commit()
                restart += 1

                restar_stock_producto(npro, cant)

    connection.close()

    mensaje = "Se actualizaron {} registros en la base de datos correctamente.".format(restart)

    # Mostrar una ventana emergente con el mensaje
    messagebox.showinfo("Éxito", mensaje)

    print("\nSe actualizaron {} registros en la base de datos correctamente.".format(restart))

def generar_boleta():
    resultados = datos_boleta('Logistica.db') #llama a la funcion y guarda los resultados en resultados
    generar_comprobantes(resultados)

    fecha_comprobante = dt.datetime.now().strftime("%Y-%m-%d") #obtiene la fecha actual y lo pone en formato YYYY-MM-DD la guarda en la variable

    # abre el navegador
    webbrowser.open('comprobantes.html')


conn = sqlite3.connect('logistica.db')
cursor = conn.cursor()


consulta = """
SELECT
    p.ncli AS NumeroDeCliente,
    pr.PRODU AS NombreDelProducto,
    pr.IMPORTE AS Valor,
    p.cant AS Cantidad,
    p.cant * pr.IMPORTE AS TotalPorProducto
FROM
    Pedidos AS p
JOIN
    Productos AS pr ON p.npro = pr.npro;
"""

cursor.execute(consulta)

# Obtener los resultados
resultados = cursor.fetchall()

# Crear un diccionario para almacenar los resultados por cliente
resultados_por_cliente = {}

# Procesa los resultados y los agrupa por cliente
for resultado in resultados:
    numero_cliente, nombre_producto, valor, cantidad, total = resultado
    if numero_cliente not in resultados_por_cliente:
        resultados_por_cliente[numero_cliente] = []
    resultados_por_cliente[numero_cliente].append((nombre_producto, valor, cantidad, total)) #junta los datos del cliente con el cliente

# Mostrar los resultados
for cliente, productos in resultados_por_cliente.items():
    print(f"Cliente {cliente}:")
    for producto in productos:
        nombre_producto, valor, cantidad, total = producto
        print(f"  Producto: {nombre_producto}, Valor: {valor}, Cantidad: {cantidad}, Total: {total}")

conn.close()

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Gestor de productos y clientes")

menu_bar = tk.Menu(ventana)
ventana.config(menu=menu_bar)

opciones_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Opciones", menu=opciones_menu)

opciones_menu.add_command(label="Actualizar Base de Datos", command=agregar_pedidos)
opciones_menu.add_command(label="Generar Boleta", command=generar_boleta) 



#crear pestañas
notebook = ttk.Notebook(ventana)
notebook.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

# Pestaña para agregar personas
frame_persona = ttk.Frame(notebook)
notebook.add(frame_persona, text="Agregar Persona")

# Pestaña para agregar productos
frame_producto = ttk.Frame(notebook)
notebook.add(frame_producto, text="Agregar Producto")

# Formulario para agregar clientes en la pestaña de agregar persona
frame_cliente = ttk.LabelFrame(frame_persona, text="Agregar Cliente", labelanchor='n')
frame_cliente.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

# Define los widgets del formulario de agregar personas
tk.Label(frame_cliente, text="Nombre del Cliente", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5)
nombre_cliente = tk.Entry(frame_cliente, width=40, font=("Helvetica", 12))
nombre_cliente.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame_cliente, text="Dirección del Cliente", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5)
direccion_cliente = tk.Entry(frame_cliente, width=40, font=("Helvetica", 12))
direccion_cliente.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame_cliente, text="Teléfono del Cliente", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5)
telefono_cliente = tk.Entry(frame_cliente, width=40, font=("Helvetica", 12))
telefono_cliente.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frame_cliente, text="Email del Cliente", font=("Helvetica", 12)).grid(row=3, column=0, padx=10, pady=5)
email_cliente = tk.Entry(frame_cliente, width=40, font=("Helvetica", 12))
email_cliente.grid(row=3, column=1, padx=10, pady=5)

tk.Label(frame_cliente, text="Localidad", font=("Helvetica", 12)).grid(row=4, column=0, padx=10, pady=5)
localidad_cliente = tk.Entry(frame_cliente, width=40, font=("Helvetica", 12))
localidad_cliente.grid(row=4, column=1, padx=10, pady=5)

tk.Label(frame_cliente, text="Domicilio de Entrega", font=("Helvetica", 12)).grid(row=5, column=0, padx=10, pady=5)
domientrega_cliente = tk.Entry(frame_cliente, width=40, font=("Helvetica", 12))
domientrega_cliente.grid(row=5, column=1, padx=10, pady=5)

tk.Label(frame_cliente, text="ID de Zonas", font=("Helvetica", 12)).grid(row=6, column=0, padx=10, pady=5)

# Definir las opciones para el menú desplegable
zonas_options = ["CABA", "NORTE GBA", "OESTE GBA", "SUR GBA"]

# Variable para almacenar la selección del usuario
id_zonas_var = tk.StringVar()
id_zonas_var.set(zonas_options[0])  # Establecer un valor predeterminado

# Crear el menú desplegable
id_zonas_menu = ttk.Combobox(frame_cliente, textvariable=id_zonas_var, values=zonas_options)
id_zonas_menu.grid(row=6, column=1, padx=10, pady=5)


tk.Label(frame_cliente, text="ID del Vendedor", font=("Helvetica", 12)).grid(row=7, column=0, padx=10, pady=5)
id_vendedor_cliente = tk.Entry(frame_cliente, width=40, font=("Helvetica", 12))
id_vendedor_cliente.grid(row=7, column=1, padx=10, pady=5)

tk.Label(frame_cliente, text="CUIT", font=("Helvetica", 12)).grid(row=8, column=0, padx=10, pady=5)
cuit_cliente = tk.Entry(frame_cliente, width=40, font=("Helvetica", 12))
cuit_cliente.grid(row=8, column=1, padx=10, pady=5)

tk.Label(frame_cliente, text="Deuda (0 o 1)", font=("Helvetica", 12)).grid(row=9, column=0, padx=10, pady=5)
deuda_cliente = tk.Entry(frame_cliente, width=40, font=("Helvetica", 12))
deuda_cliente.grid(row=9, column=1, padx=10, pady=5)

boton_agregar_cliente = ttk.Button(frame_cliente, text="Agregar Cliente", command=agregar_cliente)
boton_agregar_cliente.grid(row=10, columnspan=2, padx=10, pady=10)

# Formulario para agregar productos en la pestaña de agregar producto
frame_producto = ttk.LabelFrame(frame_producto, text="Agregar Producto", labelanchor='n')
frame_producto.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')


tk.Label(frame_producto, text="Nombre del Producto", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5)
nombre_producto_entry = tk.Entry(frame_producto, width=40, font=("Helvetica", 12))
nombre_producto_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame_producto, text="Descripción del Producto", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5)
descripcion_producto_entry = tk.Entry(frame_producto, width=40, font=("Helvetica", 12))
descripcion_producto_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame_producto, text="Precio Unitario", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5)
precio_producto_entry = tk.Entry(frame_producto, width=40, font=("Helvetica", 12))
precio_producto_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frame_producto, text="Stock del Producto", font=("Helvetica", 12)).grid(row=3, column=0, padx=10, pady=5)
stock_producto_entry = tk.Entry(frame_producto, width=40, font=("Helvetica", 12))
stock_producto_entry.grid(row=3, column=1, padx=10, pady=5)

tk.Label(frame_producto, text="ID del Proveedor", font=("Helvetica", 12)).grid(row=4, column=0, padx=10, pady=5)
id_proveedor_entry = tk.Entry(frame_producto, width=40, font=("Helvetica", 12))
id_proveedor_entry.grid(row=4, column=1, padx=10, pady=5)

# Botón para agregar un producto
boton_agregar_producto = ttk.Button(frame_producto, text="Agregar Producto", command=agregar_producto)
boton_agregar_producto.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Ejecutar el bucle principal
ventana.mainloop()