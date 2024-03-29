import random
from grafo import Grafo
from heap import Heap
from cola import Cola

INFINITO = float("inf")
D = 0.85 # Coeficiente de amortiguación para Pagerank
E = 0.0001 # Diferencia de convergencia para Pagerank

def reconstruir_camino(destino, padres):
    """Devuelve una lista ordenada con el camino desde origen
    hasta destino."""
    camino = [destino]
    v = destino
    while padres[v] != None:
        camino.append(padres[v])
        v = padres[v]
    camino.reverse()
    return camino

def obtener_camino_minimo(grafo, peso, origen, destino=None):
    """Recibe un grafo, la clave del vértice origen y la del destino,
    el tipo de peso a tener en cuenta, y devuelve un camino mínimo
    aplicando el algoritmo de Dijkstra. Si no se recibe un destino,
    devuelve los caminos mínimos desde origen hasta todos los demás
    vértices del grafo."""
    distancias, padres = {}, {}
    for v in grafo:
        distancias[v] = INFINITO
    distancias[origen] = 0
    padres[origen] = None
    q = Heap()
    q.encolar(origen, distancias[origen])
    while not q.esta_vacio():
        v = q.desencolar()
        if v == destino:
            return (reconstruir_camino(destino, padres), distancias[v])
        for w in grafo.obtener_adyacentes(v):
            if distancias[v] + grafo.obtener_peso_union(v, w)[peso] < distancias[w]:
                distancias[w] = distancias[v] + grafo.obtener_peso_union(v, w)[peso]
                padres[w] = v
                q.encolar(w, distancias[w])
    return distancias, padres

def escalas_minimas_bfs(grafo, origen, destino=None):
    """Recibe un grafo, la clave del vertice origen y la del destino,
    y devuelve un camino con la minima cantidad de escalas aplicando
    el algoritmo bfs. Si no se recibe un destino, devuelve los caminos
    con menor cantidad de escalas desde origen hasta todos los demás
    vértices del grafo."""
    visitados = []
    padres, orden = {}, {}
    q = Cola()
    visitados.append(origen)
    padres[origen] = None
    orden[origen] = 0
    q.encolar(origen)
    while not q.esta_vacia():
        v = q.desencolar()
        for w in grafo.obtener_adyacentes(v):
            if w not in visitados:
                visitados.append(w)
                padres[w] = v
                orden[w] = orden[v] + 1
                q.encolar(w)
            if w == destino:
                return reconstruir_camino(destino, padres), orden[w]
    return orden, padres

def betweeness_centrality(grafo):
    """Recibe un grafo y devuelve un diccionario cent de la forma
    vertice:centralidad que sirve para encontrar el mas central"""
    cent = {}
    for v in grafo: cent[v] = 0
    for v in grafo:
        distancias, padres = escalas_minimas_bfs(grafo, v)
        cent_aux = {}
        for w in grafo: cent_aux[w] = 0
        vertices_ordenados = sorted(distancias, key=lambda i: distancias[i], reverse=True)
        for w in vertices_ordenados:
            if w == v: continue
            cent_aux[padres[w]] += 1 + cent_aux[w]
        for w in grafo:
            if w == v: continue
            cent[w] += cent_aux[w]
    return cent

def obtener_centralidad_aproximada(grafo):
    """Recibe un grafo y realiza random walks sobre él, y devuelve
    la centralidad aproximada de cada vértice."""
    centralidades = {}
    for v in grafo:
        centralidades[v] = 0
    for v in grafo:
        w = random.choice([w for w in grafo.obtener_adyacentes(v)])
        centralidades[w] += 1
    return centralidades

def obtener_pagerank(grafo):
    """Recibe un grafo, aplica el algoritmo de Pagerank y devuelve
    un diccionario con la forma vertice: centralidad_pagerank."""
    pagerank = {}
    for v in grafo:
        pagerank[v] = (1 - D) / len(grafo)
    converge = False
    while not converge:
        pagerank_actual = {}
        converge = True
        for v in grafo:
            pagerank_actual[v] = 0
            for w in grafo.obtener_adyacentes(v):
                pagerank_actual[v] += D * pagerank[w]/len(grafo.obtener_adyacentes(w))
            if abs(pagerank_actual[v] - pagerank[v]) > E:
                converge = False
        pagerank = pagerank_actual
    return pagerank

def obtener_frecuencias(grafo, centralidades, peso):
    """Recibe un grafo, un diccionario de centralidades y el índice
    del peso que contiene la cantidad de vuelos entre un aeropuerto y otro,
    y multiplica la centralidad de cada vértice por su frecuencia."""
    frecuencias = {}
    for v in centralidades:
        frecuencias[v] = 0
        for w in grafo.obtener_adyacentes(v):
            frecuencias[v] += grafo.obtener_peso_union(v, w)[peso]
        centralidades[v] *= frecuencias[v]

def obtener_viaje(grafo, origen, n):
    """Recibe un grafo, un origen y un número entero n.
    Devuelve un viaje de n lugares que comienza y finaliza
    en origen."""
    recorrido = [origen]
    visitados = set()
    distancias = {}
    for v in grafo:
        camino, distancia = escalas_minimas_bfs(grafo, v, origen)
        distancias[v] = distancia
    if not _obtener_viaje(grafo, origen, n, recorrido, visitados, distancias):
        return None
    return recorrido

def _obtener_viaje(grafo, origen, n, recorrido, visitados, distancias):
    """Función auxiliar para obtener un viaje de n lugares."""
    ultimo = recorrido[-1]
    if len(recorrido) == n:
        if origen not in grafo.obtener_adyacentes(ultimo):
            return False
        recorrido.append(origen)
        return True
    if distancias[ultimo] >= n - len(recorrido) + 1:
        # Si la distancia mínima (en escalas) es mayor a la cantidad
        # de lugares restantes para completar el recorrido,
        # no va a haber solución por este camino
        return False
    for v in grafo.obtener_adyacentes(ultimo):
        if v in visitados:
            continue
        recorrido.append(v)
        visitados.add(v)
        if _obtener_viaje(grafo, origen, n, recorrido, visitados, distancias):
            return True
        recorrido.pop()
        visitados.remove(v)
    return False

def exportar_archivo_kml(grafo, recorrido, archivo):
    """Recibe una lista con un recorrido y un archivo, y exporta
    a dicho archivo el recorrido en formato kml."""
    visitados = set()
    archivo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    archivo.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    archivo.write('    <Document>\n')
    for i in range(len(recorrido)):
        if recorrido[i] in visitados: continue
        visitados.add(recorrido[i])
        coordenadas = grafo.obtener_dato(recorrido[i])
        archivo.write('        <Placemark>\n')
        archivo.write('            <name>{}</name>\n'.format(recorrido[i]))
        archivo.write('            <Point>\n')
        archivo.write('                <coordinates>{}</coordinates>\n'.format(coordenadas))
        archivo.write('            </Point>\n')
        archivo.write('        </Placemark>\n')
    for i in range(len(recorrido) - 1):
        origen = grafo.obtener_dato(recorrido[i])
        destino = grafo.obtener_dato(recorrido[i+1])
        archivo.write('        <Placemark>\n')
        archivo.write('            <LineString>\n')
        archivo.write('                <coordinates>{} {}</coordinates>\n'.format(origen, destino))
        archivo.write('            </LineString>\n')
        archivo.write('        </Placemark>\n')
    archivo.write('    </Document>\n')
    archivo.write('</kml>\n')

def optimizar_rutas(grafo, peso):
    """Recibe un grafo, aplica el algoritmo de Prim y devuelve un
    árbol de tendido mínimo."""
    vertice = grafo.obtener_vertice()
    visitados = {vertice}
    q = Heap()
    for w in grafo.obtener_adyacentes(vertice):
        q.encolar((vertice, w), grafo.obtener_peso_union(vertice, w)[peso])
    arbol = Grafo()
    for v in grafo:
        arbol.agregar_vertice(v, grafo.obtener_dato(v))
    while not q.esta_vacio():
        v, w = q.desencolar()
        if w in visitados:
            continue
        arbol.agregar_arista(v, w, grafo.obtener_peso_union(v, w))
        visitados.add(w)
        for u in grafo.obtener_adyacentes(w):
            if u not in visitados:
                q.encolar((w, u), grafo.obtener_peso_union(w, u)[peso])
    return arbol

def exportar_aerolinea(grafo, archivo, rutas=None):
    """Recibe un grafo representando una aerolínea y  un archivo, y
    exporta al archivo los vuelos existentes en la aerolínea, de la
    forma aeropuerto_i,aeropuerto_j,tiempo,precio,cantidad_vuelos.
    Adicionalmente recibe una lista y guarda en ella las rutas
    entre vértices."""
    visitados = set()
    for v in grafo:
        visitados.add(v)
        for w in grafo.obtener_adyacentes(v):
            if w in visitados: continue
            tiempo, precio, vuelos = grafo.obtener_peso_union(v, w)
            archivo.write(",".join([v, w, str(tiempo), str(precio), str(vuelos)])+"\n")
            if rutas != None:
                rutas.append(v)
                rutas.append(w)

def obtener_n_mayores(diccionario, n, reverse = False):
    """Recibe un diccionario clave: valor y devuelve una lista con
    las n mayores claves, ordenada descendente por defecto o
    ascendentemente, con respecto a sus valores."""
    q = Heap()
    for clave in diccionario:
        if len(q) < n:
            q.encolar(clave, diccionario[clave])
        elif diccionario[clave] >= diccionario[q.ver_minimo()]:
            q.desencolar()
            q.encolar(clave, diccionario[clave])
    resultado = []
    while not q.esta_vacio():
        resultado.append(q.desencolar())
    if reverse:
        resultado.reverse()
    return resultado

def orden_topologico(grafo):
    """Recibe un grafo dirigido y devuelve una lista con un
    ordenamiento topológico de los vértices del mismo."""
    visitados = set()
    resultado = []
    for v in grafo:
        if v in visitados:
            continue
        _orden_topologico(grafo, v, resultado, visitados)
    resultado.reverse()
    return resultado

def _orden_topologico(grafo, origen, lista, visitados):
    """Función auxiliar para orden_topologico."""
    visitados.add(origen)
    for v in grafo.obtener_adyacentes(origen):
        if v in visitados:
            continue
        _orden_topologico(grafo, v, lista, visitados)
    lista.append(origen)