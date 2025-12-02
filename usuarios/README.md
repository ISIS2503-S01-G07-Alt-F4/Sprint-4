# Sprint-2
El sprint 2 :)

## Tutorial de uso de Docker
1. Instalar Docker Desktop desde [aquí](https://www.docker.com/products/docker-desktop/) (Probablemente ya lo tengan por TIC).
2. Correr Docker Desktop.
3. Abrir la terminal.
4. Ejecutar el comando `docker-compose up --build` en la terminal, en la carpeta donde está este proyecto.
5. Esperar a que termine de correr (la primera vez puede tardar un poco más).
6. Usarlo normalmente como si fuera un proyecto de Django normal.
7. Cuando lo vuelvan a usar, solo necesitan correr `docker-compose up` (sin el `--build`).
8. Para ejecutar algun comando en la terminal del contenedor de Django, ejecutar `docker-compose exec django bash`.
9. Para salir de la terminal del contenedor, ejecutar `exit`.
10. Ser feliz :D