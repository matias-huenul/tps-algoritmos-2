#include <stdlib.h>
#include "heap.h"

#define CAPACIDAD_INICIAL 10
#define FACTOR_REDIMENSION 2
#define COND_ACHICAR 4

struct heap {
	void** datos;
	size_t capacidad;
	size_t cantidad;
	cmp_func_t cmp;
};

/******************************************************************************
 *                          FUNCIONES AUXILIARES
 *****************************************************************************/

size_t obtener_padre(size_t pos) {
	return (pos - 1) / 2;
}

size_t obtener_hijo_izq(size_t pos) {
	return 2 * pos + 1;
}

size_t obtener_hijo_der(size_t pos) {
	return 2 * pos + 2;
}

void swap(void** arreglo, size_t a, size_t b) {
	void* aux = arreglo[a];
	arreglo[a] = arreglo[b];
	arreglo[b] = aux;
}

void upheap(void* arreglo[], size_t pos, cmp_func_t cmp) {
	if (pos == 0) return;
	size_t padre = obtener_padre(pos);
	if (cmp(arreglo[padre], arreglo[pos]) > 0)
		return;
	swap(arreglo, padre, pos);
	upheap(arreglo, padre, cmp);
}

void downheap(void* arreglo[], size_t n, size_t pos, cmp_func_t cmp) {
	size_t maximo = pos;
	size_t izq = obtener_hijo_izq(pos);
	size_t der = obtener_hijo_der(pos);
	if (izq < n && cmp(arreglo[izq], arreglo[maximo]) > 0)
		maximo = izq;
	if (der < n && cmp(arreglo[der], arreglo[maximo]) > 0)
		maximo = der;
	if (maximo == pos) return;
	swap(arreglo, pos, maximo);
	downheap(arreglo, n, maximo, cmp);
}

void heapify(void* arreglo[], size_t n, cmp_func_t cmp) {
	for (size_t i = n; i > 0; i--) {
		downheap(arreglo, n, i-1, cmp);
	}
}

bool heap_redimensionar(heap_t* heap, size_t nueva_capacidad) {
	void** datos_nuevo = realloc(heap->datos, nueva_capacidad * sizeof(void*));
	if (!datos_nuevo) return false;
	heap->datos = datos_nuevo;
	heap->capacidad = nueva_capacidad;
	return true;
}

/******************************************************************************
 *                          PRIMITIVAS DEL HEAP
 *****************************************************************************/

heap_t* heap_crear(cmp_func_t cmp) {
	heap_t* heap = malloc(sizeof(heap_t));
	if (!heap) return NULL;
	heap->capacidad = CAPACIDAD_INICIAL;
	heap->datos = malloc(heap->capacidad * sizeof(void*));
	if (!heap->datos) {
		free(heap);
		return NULL;
	}
	heap->cantidad = 0;
	heap->cmp = cmp;
	return heap;
}

heap_t* heap_crear_arr(void* arreglo[], size_t n, cmp_func_t cmp) {
	heap_t* heap = malloc(sizeof(heap_t));
	if (!heap) return NULL;
	heapify(arreglo, n, cmp);
	heap->datos = arreglo;
	heap->capacidad = n;
	heap->cantidad = n;
	heap->cmp = cmp;
	return heap;
}

bool heap_encolar(heap_t* heap, void* elem) {
	if (!elem) return false;
	if (heap->cantidad == heap->capacidad) {
		if(!heap_redimensionar(heap, heap->cantidad*FACTOR_REDIMENSION))
			return false;
	}
	heap->datos[heap->cantidad] = elem;
	upheap(heap->datos, heap->cantidad, heap->cmp);
	heap->cantidad++;
	return true;
}

size_t heap_cantidad(const heap_t* heap){
	return heap->cantidad;
}

bool heap_esta_vacio(const heap_t* heap){
	return heap->cantidad == 0;
}

void heap_destruir(heap_t* heap, void destruir_elemento(void* e)){
	if (destruir_elemento){
		for(size_t i=0; i<(heap->cantidad); i++){
			destruir_elemento(heap->datos[i]);
		}	
	}
	free(heap->datos);
	free(heap);
}

void* heap_ver_max(const heap_t* heap){
	if (heap_esta_vacio(heap)) return NULL;
	return heap->datos[0];
}

void* heap_desencolar(heap_t* heap){
	if (heap_esta_vacio(heap)) return NULL;
	void* desencolado = heap->datos[0];
	heap->datos[0] = NULL;
	swap(heap->datos, 0, heap->cantidad-1);
	heap->cantidad--;
	downheap(heap->datos, heap->cantidad, 0, heap->cmp);
	if (COND_ACHICAR*heap->cantidad == heap->capacidad){
		if (!heap_redimensionar(heap, heap->cantidad/FACTOR_REDIMENSION))
			return false;
	}
	return desencolado;
}

void heap_sort(void* arreglo[], size_t n, cmp_func_t cmp) {
	for (size_t i = n; i > 1; i--) {
		heapify(arreglo, i, cmp);
		swap(arreglo, 0, i-1);
	}
}