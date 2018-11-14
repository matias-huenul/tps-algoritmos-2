#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "strutil.h"
#include "sistema.h"
#include "vuelo.h"

// Posiciones de cada dato en el csv
#define CODIGO 0
#define PRIORIDAD 5
#define HORA 6

vuelo_t* procesar_linea(char* linea) {
	char** datos = split(linea, ',');
	char* codigo = datos[CODIGO];
	int prioridad = atoi(datos[PRIORIDAD]);
	char* hora = datos[HORA];
	vuelo_t* vuelo = vuelo_crear(codigo, prioridad, hora, datos);
	free_strv(datos);
	return vuelo;
}

bool agregar_archivo(sistema_t* sistema, char* comando[]) {
	FILE* archivo = fopen(comando[1], "r");
	if (!archivo) return false;
	char* linea = NULL;
	size_t tam = 0;
	size_t cant;
	while ((cant = getline(&linea, &tam, archivo)) != EOF) {
		if (linea[cant-1] == '\n')
			linea[cant-1] = '\0';
		vuelo_t* vuelo = procesar_linea(linea);
		sistema_agregar_vuelo(sistema, vuelo);
	}
	free(linea);
	fclose(archivo);
	return true;
}

void imprimir_tablero(vuelo_t** vuelos_tablero){
	for(size_t i=0; vuelos_tablero[i]!=NULL; i++){
		printf("%s - %s\n", vuelos_tablero[i][HORA], vuelos_tablero[i][CODIGO]);
	}
}

bool ver_tablero(sistema_t* sistema, char* comando[]){
	int cant_vuelos = atoi(comando[1]);
	if (cant_vuelos < 1) return false;
	char* modo = comando[2];
	if (strcmp(modo,"asc") != 0 && strcmp(modo,"desc") != 0) return false;
	char fecha_desde = comando[3];
	char fecha_hasta = comando[4];
	char* fecha_desde_split = split(comando[3],"T");
	char* fecha_hasta_split = split(comando[4],"T");
	if (strcmp(fecha_hasta_split[0], fecha_desde_split[0]) < 0) return false;
	vuelo_t** vuelos_tablero = sistema_ver_tablero(sistema, cant_vuelos, modo, fecha_desde, fecha_hasta);
	imprimir_tablero(vuelos_tablero);

	free_strv(fecha_desde_split);
	free_strv(fecha_hasta_split);
}

bool info_vuelo(const sistema_t* sistema, char* comando[]) {
	vuelo_t* vuelo = sistema_ver_vuelo(sistema, comando[1]);
	if (!vuelo) return false;
	printf("%s\n", vuelo_info(vuelo));
	return true;
}

bool prioridad_vuelos(sistema_t* sistema, char* comando[]) {
	if (strspn(comando[1], "0123456789") != strlen(comando[1]))
		return false; // Si k no es un número
	heap_t* heap = sistema_prioridades(sistema, atoi(comando[1]));
	while (!heap_esta_vacio(heap)) {
		vuelo_t* vuelo = heap_desencolar(heap);
		printf("%d - %s\n", vuelo_prioridad(vuelo), vuelo_codigo(vuelo));
	}
	// En la página dice que las prioridades tienen que ser impresas de
	// mayor a menor, así que hay que invertir esto
	heap_destruir(heap, NULL);
	return true;
}

bool procesar_comando(sistema_t* sistema, char* entrada) {
	if (!entrada) return false;
	bool ok = false;
	char** comando = split(entrada, ' ');
	if (strcmp(comando[0], "agregar_archivo") == 0)
		ok = agregar_archivo(sistema, comando);
	else if (strcmp(comando[0], "ver_tablero") == 0)
		ok = ver_tablero(sistema, comando);
	else if (strcmp(comando[0], "info_vuelo") == 0)
		ok = info_vuelo(sistema, comando);
	else if (strcmp(comando[0], "prioridad_vuelos") == 0)
		ok = prioridad_vuelos(sistema, comando);
	else if (strcmp(comando[0], "borrar") == 0)
		ok = borrar(sistema, comando);
	free_strv(comando);
	return ok;
}

/* Función principal del programa. */
int main(void) {
	sistema_t* sistema = sistema_crear();
	char* entrada = NULL;
	size_t tam = 0;
	size_t cant;
	while ((cant = getline(&entrada, &tam, stdin)) != EOF) {
		if (entrada[cant-1] == '\n') // Agrego esto porque getline da problemas si hay un \n al final
			entrada[cant-1] = '\0';
		if (procesar_comando(sistema, entrada)) {
			printf("OK\n");
		} else {
			fprintf(stderr, "Error en comando %s\n", entrada);
		}
	}
	free(entrada);
	sistema_destruir(sistema);
	return 0;
}