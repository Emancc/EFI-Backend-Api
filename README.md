# EFI Backend API

Backend en **Python (Flask)** para la E.F.I. (Entrega Final Integradora).  
Incluye autenticación y CRUD típicos (Usuarios, Categorías, Posts y Comentarios), con SQLAlchemy/Marshmallow y configuración local en `instance/`.

## Integrantes 

- Cepeda Cáceres Emanuel https://github.com/Emancc
- Arballo Federico Ezequiel https://github.com/FedeAr25
- Joaquin Ramon Rodríguez https://github.com/joaquindevops

## Stack y requisitos

- **Python** 3.10+ (recomendado 3.11)
- **Flask** (+ extensiones habituales: SQLAlchemy, Marshmallow, JWT, Migrate, CORS)
- **SQLite** por defecto (o cualquier motor vía `DATABASE_URL`)
- `pip` y `venv` para dependencias
- **Requirements.txt** se proporciona un archivo de texto con las dependencias del proyecto

---

## Instalación

Clonar y crear entorno virtual:

```bash
git clone https://github.com/Emancc/EFI-Backend-Api.git
cd EFI-Backend-Api

# Linux/Mac
python -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

#instalar dependencias
pip install -r requirements.txt

#crear la base de datos en mysql con MySqlYog o similar este proyecto a sido realizado con XAMPP.
- ** el nombre de la base de datos es db_blog **
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/** de otro modo cambiar el nombre de la base e introducirlo aqui** '

#o utilizar la base de datos de ITEC
app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql+pymysql://BD2021:BD2021itec@143.198.156.171:3306/EFI_python2')


#Categorias para la base de datos recomendada-- nota no tiene categorias internas 
INSERT INTO category (name, slug, description) VALUES
('Desarrollo Web','desarrollo-web','Categoría: Desarrollo Web'),
('Frontend','frontend','Categoría: Frontend'),
('Backend','backend','Categoría: Backend'),
('DevOps','devops','Categoría: DevOps'),
('Ciencia de Datos','ciencia-de-datos','Categoría: Ciencia de Datos'),
('Machine Learning','machine-learning','Categoría: Machine Learning'),
('Visualización de Datos','visualizacion-de-datos','Categoría: Visualización de Datos'),
('Python','python','Categoría: Python'),
('R y Estadística','r-y-estadistica','Categoría: R y Estadística'),
('Arduino & IoT','arduino-iot','Categoría: Arduino & IoT'),
('Electrónica','electronica','Categoría: Electrónica'),
('Bases de Datos','bases-de-datos','Categoría: Bases de Datos'),
('APIs & Microservicios','apis-microservicios','Categoría: APIs & Microservicios'),
('Seguridad','seguridad','Categoría: Seguridad'),
('Testing & QA','testing-qa','Categoría: Testing & QA'),
('E-commerce','ecommerce','Categoría: E-commerce'),
('Emprendimiento','emprendimiento','Categoría: Emprendimiento'),
('Cloud & Infra','cloud-infra','Categoría: Cloud & Infra'),
('Linux & Dev Tools','linux-dev-tools','Categoría: Linux & Dev Tools'),
('Proyectos EFI','proyectos-efi','Categoría: Proyectos EFI');

#inicializar el proyecto con
flask run --reload
