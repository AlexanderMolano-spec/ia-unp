#!/bin/bash

# Script de utilidad para levantar la infraestructura EI-UNP
# Autor: Senior DevOps Engineer

echo "INFO: Iniciando infraestrucura de datos EI-UNP..."

# Asegurar que estamos en el directorio raíz o movernos según sea necesario
# (Asumiendo ejecución desde la raíz del repo)

docker compose up -d --build

echo "SUCCESS: Infraestructura desplegada en segundo plano."
echo "------------------------------------------------------------"
echo "Knowledge DB: http://localhost:14010"
echo "Memory DB:    http://localhost:14013"
echo "Scraper:      http://localhost:14014"
echo "------------------------------------------------------------"
echo "Ejecute 'docker compose logs -f' para ver el estado de los servicios."
