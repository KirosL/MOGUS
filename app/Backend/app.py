# ========== IMPORTACIONES ==========
from flask import Flask, abort, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import pandas as pd
import os
import io
import tempfile
from functools import wraps
from werkzeug.security import generate_password_hash

# Para exportar PDF
from weasyprint import HTML, CSS

# Para gráficos
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

def crear_app():
    # ========== CONFIGURACIÓN DE LA APP ==========
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///procesos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)

    # ========== FUNCIONES AUXILIARES ==========
    def get_colombian_time():
        """Retorna la hora actual en la zona horaria de Colombia."""
        colombian_tz = pytz.timezone('America/Bogota')
        return datetime.now(colombian_tz)

    def get_model_by_process(proceso):
        """Devuelve el modelo correspondiente al proceso"""
        if proceso == 'Parques_Urbanos':
            return Parque_Urbano
        elif proceso == 'Corredores_Ecologicos':
            return Corredor_Urbano
        return None

    # ========== DECORADORES ==========
    def handle_errors(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('home'))
        return decorated_function

    # ========== MODELOS ==========
    class Parque_Urbano(db.Model):
        id_Fase = db.Column(db.Integer, primary_key=True)
        nombre_fase = db.Column(db.String(100), nullable=False)
        tipo_fase = db.Column(db.String(100), nullable=False)
        descripcion = db.Column(db.Text, nullable=False)
        indicador = db.Column(db.String(100), nullable=False)
        nombre_revisor = db.Column(db.String(100), nullable=False)
        area_verde = db.Column(db.Integer, nullable=False)
        area_total = db.Column(db.Integer, nullable=False)
        porcentaje_indicador = db.Column(db.Integer, nullable=False)
        viabilidad = db.Column(db.Text, nullable=False)
        fecha_actualizacion = db.Column(db.DateTime(timezone=True), default=get_colombian_time, onupdate=get_colombian_time)
        fecha_creacion = db.Column(db.DateTime(timezone=True), default=get_colombian_time)

        def calcular_porcentaje(self):
            if self.area_total > 0:
                return round((self.area_verde / self.area_total) * 100, 2)
            return 0

        def calcular_viabilidad(self):
            porcentaje = self.calcular_porcentaje() / 100
            if porcentaje >= 0.7:
                return "Viable ✅"
            elif porcentaje >= 0.4:
                return "Medianamente viable ⚠️"
            return "No viable ❌"

        def save(self, db):
            self.porcentaje_indicador = self.calcular_porcentaje()
            self.viabilidad = self.calcular_viabilidad()
            db.session.add(self)
            db.session.commit()
            return self

        def to_dict(self):
            return {
                'id_Fase': self.id_Fase,
                'nombre_fase': self.nombre_fase,
                'tipo_fase': self.tipo_fase,
                'descripcion': self.descripcion,
                'indicador': self.indicador,
                'nombre_revisor': self.nombre_revisor,
                'area_verde': self.area_verde,
                'area_total': self.area_total,
                'porcentaje_indicador': self.porcentaje_indicador,
                'viabilidad': self.viabilidad,
                'fecha_actualizacion': self.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S %Z')
            }


    class Corredor_Urbano(Parque_Urbano):
        __tablename__ = 'corredor_urbano'
        id_Fase = db.Column(db.Integer, db.ForeignKey('parque__urbano.id_Fase'), primary_key=True)

    # ========== RUTAS PRINCIPALES ==========
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/diagnostico/<proceso>')
    def diagnostico(proceso):
        if proceso not in ['Parques_Urbanos', 'Corredores_Ecologicos']:
            abort(404)
        
        modelo = get_model_by_process(proceso)
        if not modelo:
            flash('Proceso no válido', 'danger')
            return redirect(url_for('home'))

        try:
            fases = modelo.query.all()
            return render_template('proceso/diagnostico.html', fases=fases, now=get_colombian_time(), Proceso=proceso)
        except Exception as e:
            flash(f'Error al cargar las fases: {str(e)}', 'danger')
            return render_template('proceso/diagnostico.html', fases=[], now=get_colombian_time(), Proceso=proceso)

    @app.route('/Parques_Urbanos')
    def Parques_Urbanos():
        try:
            fases = Parque_Urbano.query.all()
            return render_template('proceso/Parques_Urbanos.html', fases=fases, now=datetime.now(), Proceso="Parques_Urbanos")
        except Exception as e:
            flash(f'Error al cargar las fases: {str(e)}', 'danger')
            return render_template('proceso/Parques_Urbanos.html', fases=[], now=datetime.now(), Proceso="Parques_Urbanos")

    @app.route('/Corredores_Ecologicos')
    def Corredores_Ecologicos():
        try:
            fases = Corredor_Urbano.query.all()
            return render_template('proceso/Corredores_Ecologicos.html', fases=fases, now=datetime.now(), Proceso="Corredores_Ecologicos")
        except Exception as e:
            flash(f'Error al cargar las fases: {str(e)}', 'danger')
            return render_template('proceso/Corredores_Ecologicos.html', fases=[], now=datetime.now(), Proceso="Corredores_Ecologicos")

    @app.route('/resultado/<proceso>')
    def resultado(proceso):
        try:
            return render_template('proceso/resultado.html', Proceso=proceso, now=datetime.now())
        except Exception as e:
            flash(f'Error al cargar los resultados: {str(e)}', 'danger')
            return render_template('index.html', now=datetime.now())

    # ========== RUTAS DE EJEMPLOS Y OTRAS ==========
    @app.route('/ejemplosParques')
    def ejemploParque():
        try:
            return render_template('ejemplo/ejemplo_Parques.html', now=datetime.now(), pagina_activa='parques')
        except Exception as e:
            flash(f'Error al cargar los ejemplos: {str(e)}', 'danger')
            return redirect(url_for('home'))

    @app.route('/ejemplosCorredores')
    def ejemploCorredor():
        try:
            return render_template('ejemplo/ejemplo_Corredores.html', now=datetime.now(), pagina_activa='corredores')
        except Exception as e:
            flash(f'Error al cargar los ejemplos: {str(e)}', 'danger')
            return redirect(url_for('home'))

    @app.route('/aboutUs')
    def about():
        try:
            return render_template('about_us.html', now=datetime.now())
        except Exception as e:
            flash(f'Error al cargar la página: {str(e)}', 'danger')
            return redirect(url_for('home'))

    def safe_int(value, default=0):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def construir_fase_from_form(model_class, form):
        return model_class(
            nombre_fase=form.get('nombre_fase', '').strip(),
            tipo_fase=form.get('tipo_fase', '').strip(),
            descripcion=form.get('descripcion', '').strip(),
            indicador=form.get('indicador', '').strip(),
            nombre_revisor=form.get('nombre_revisor', '').strip(),
            area_verde=safe_int(form.get('area_verde')),
            area_total=safe_int(form.get('area_total')),
            porcentaje_indicador=safe_int(form.get('porcentaje_indicador')),
            viabilidad=form.get('viabilidad', '').strip()
        )

    @app.route('/crear/<proceso>', methods=['GET', 'POST'])
    @handle_errors
    def crear(proceso):
        if proceso not in ['Parques_Urbanos', 'Corredores_Ecologicos']:
            flash('Proceso no válido', 'danger')
            return redirect(url_for('home'))

        if request.method == 'POST':
            try:
                print("Form Data:", request.form)

                modelo = get_model_by_process(proceso)
                if not modelo:
                    flash('Modelo no encontrado para el proceso', 'danger')
                    return redirect(url_for(proceso))

                nueva_fase = construir_fase_from_form(modelo, request.form)
                nueva_fase.save(db)

                flash('Fase creada con éxito', 'success')
                return redirect(url_for(proceso))

            except Exception as e:
                db.session.rollback()
                import traceback
                traceback.print_exc()
                flash(f'Error al crear la fase: {str(e)}', 'danger')
                return redirect(url_for(proceso))

        modelo = get_model_by_process(proceso)
        fases = modelo.query.all() if modelo else []
        return render_template(f'proceso/{proceso}.html', fases=fases, now=get_colombian_time(), Proceso=proceso)

    @app.route('/editar/<proceso>/<int:id>', methods=['GET', 'POST'])
    @handle_errors
    def editar(proceso, id):
        modelo = get_model_by_process(proceso)
        
        if not modelo:
            flash('Proceso no válido', 'danger')
            return redirect(url_for('home'))
        
        fase = modelo.query.get_or_404(id)
        
        if request.method == 'POST':
            try:
                fase.nombre_fase = request.form.get('nombre_fase', '').strip() or fase.nombre_fase
                fase.tipo_fase = request.form.get('tipo_fase', '').strip() or fase.tipo_fase
                fase.descripcion = request.form.get('descripcion', '').strip() or fase.descripcion
                fase.indicador = request.form.get('indicador', '').strip() or fase.indicador
                fase.nombre_revisor = request.form.get('nombre_revisor', '').strip() or fase.nombre_revisor
                
                fase.area_verde = safe_int(request.form.get('area_verde', fase.area_verde))
                fase.area_total = safe_int(request.form.get('area_total', fase.area_total))

                fase.porcentaje_indicador = fase.calcular_porcentaje()
                fase.viabilidad = fase.calcular_viabilidad()

                db.session.commit()
                flash('Fase actualizada con éxito', 'success')
                return redirect(url_for(proceso))
            
            except ValueError as e:
                flash(f'Error en los datos: {str(e)}', 'danger')
                return redirect(url_for(proceso))
            
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar la fase: {str(e)}', 'danger')
                return redirect(url_for(proceso))
        
        fases = modelo.query.all()
        return render_template(f'proceso/{proceso}.html', fase=fase, fases=fases, now=get_colombian_time(), Proceso=proceso)

    @app.route('/ver/<proceso>/<int:id>', methods=['GET'])
    @handle_errors
    def ver(proceso, id):
        modelo = get_model_by_process(proceso)
        
        if not modelo:
            flash('Proceso no válido', 'danger')
            return redirect(url_for('home'))

        fase = modelo.query.get_or_404(id)
        fases = modelo.query.all()
        
        return render_template(f'proceso/{proceso}.html', fase=fase, fases=fases, now=get_colombian_time(), Proceso=proceso)


    @app.route('/eliminar/<proceso>/<int:id>', methods=['POST'])
    @handle_errors
    def eliminar(proceso, id):
        """
        Elimina una fase específica.
        :param proceso: Identificador del proceso
        :param id: ID de la fase a eliminar
        """
        modelo = get_model_by_process(proceso)
        
        if not modelo:
            flash('Proceso no válido', 'danger')
            return redirect(url_for('home'))
        
        try:
            fase = modelo.query.get_or_404(id)
            nombre = fase.nombre_fase  # Guardamos el nombre para el mensaje
            
            db.session.delete(fase)
            db.session.commit()
            flash(f'Fase "{nombre}" eliminada con éxito', 'success')
            return redirect(url_for(proceso))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al eliminar la fase: {str(e)}', 'danger')
            return redirect(url_for(proceso))
        

    # Añadir estas importaciones en app.py:
    import matplotlib
    matplotlib.use('Agg')  # Para usar matplotlib sin un servidor gráfico
    import matplotlib.pyplot as plt
    import numpy as np
    import os

    def generar_graficos_base64(fases):
        """Genera gráficos y devuelve sus representaciones base64"""
        graficos = {}
        
        # Obtener datos
        nombres_fases = [fase.nombre_fase for fase in fases]
        porcentajes = [fase.porcentaje_indicador for fase in fases]
        areas_verdes = [fase.area_verde for fase in fases]
        areas_totales = [fase.area_total for fase in fases]
        
        # Contar tipos de viabilidad
        viables = sum(1 for fase in fases if "Viable ✅" in fase.viabilidad)
        medio_viables = sum(1 for fase in fases if "Medianamente viable ⚠️" in fase.viabilidad)
        no_viables = sum(1 for fase in fases if "No viable ❌" in fase.viabilidad)
        
        # Estilo general para los gráficos
        plt.style.use('seaborn-v0_8-pastel')
        plt.rcParams.update({
            'font.family': 'Arial',
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'figure.figsize': (8, 5),
            'figure.dpi': 100
        })
        
        # 1. Gráfico de Barras - Porcentaje de Indicador por Fase
        plt.figure()
        bars = plt.bar(nombres_fases, porcentajes, color='#4CAF50', alpha=0.7)
        plt.title('Porcentaje de Indicador por Fase')
        plt.xlabel('Fases')
        plt.ylabel('Porcentaje (%)')
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 100)
        plt.tight_layout()
        
        # Añadir etiquetas de valor
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # Guardar en BytesIO y convertir a base64
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        graficos['indicador_barras'] = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        # 2. Gráfico de Barras Apiladas - Área Verde vs Total
        plt.figure()
        areas_no_verdes = [area_total - area_verde for area_total, area_verde in zip(areas_totales, areas_verdes)]
        
        ax = plt.subplot(111)
        ancho = 0.7
        
        # Calcular porcentajes
        porcentajes_verde = [(area_verde / area_total * 100) if area_total > 0 else 0 
                            for area_verde, area_total in zip(areas_verdes, areas_totales)]
        
        # Barras apiladas
        p1 = ax.bar(nombres_fases, areas_verdes, ancho, color='#4CAF50', alpha=0.7, label='Área Verde')
        p2 = ax.bar(nombres_fases, areas_no_verdes, ancho, bottom=areas_verdes, 
                    color='#9E9E9E', alpha=0.7, label='Área No Verde')
        
        plt.title('Comparación de Área Verde vs Área Total')
        plt.xlabel('Fases')
        plt.ylabel('Área (m²)')
        plt.xticks(rotation=45, ha='right')
        plt.legend(loc='upper right')
        
        # Añadir porcentajes como texto
        for i, p in enumerate(p1):
            width = p.get_width()
            height = p.get_height()
            x = p.get_x() + width/2
            y = height/2
            ax.text(x, y, f'{porcentajes_verde[i]:.1f}%', ha='center', va='center', color='white', fontweight='bold')
        
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        graficos['area_barras'] = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        # 3. Gráfico Circular (Donut) - Distribución de Viabilidad
        plt.figure()
        labels = ['Viable', 'Medianamente\nviable', 'No viable']
        sizes = [viables, medio_viables, no_viables]
        colors = ['#4CAF50', '#FFC107', '#F44336']
        
        # Crear un gráfico tipo donut
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                startangle=90, wedgeprops=dict(width=0.4))
        
        # Añadir círculo en el centro para crear efecto donut
        centre_circle = plt.Circle((0,0),0.3,fc='white')
        plt.gca().add_artist(centre_circle)
        
        plt.axis('equal')
        plt.title('Distribución de la Viabilidad de las Fases')
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        graficos['viabilidad_donut'] = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        # 4. Gráfico de Líneas - Evolución del Indicador
        plt.figure()
        plt.plot(nombres_fases, porcentajes, 'o-', color='#FF9800', linewidth=2, markersize=8)
        plt.title('Evolución del Indicador a lo Largo de las Fases')
        plt.xlabel('Fases')
        plt.ylabel('Porcentaje de Indicador (%)')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Añadir los valores sobre los puntos
        for i, porcentaje in enumerate(porcentajes):
            plt.annotate(f'{porcentaje:.1f}%', 
                        (i, porcentaje), 
                        textcoords="offset points",
                        xytext=(0,10), 
                        ha='center')
        
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        graficos['evolucion_lineas'] = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return graficos

    @app.route('/generar_pdf/<proceso>', methods=['GET'])
    @handle_errors
    def generar_pdf(proceso):
        modelo = get_model_by_process(proceso)
        
        if not modelo:
            flash('Proceso no válido para generación de PDF', 'danger')
            return redirect(url_for('home'))
        
        try:
            # Obtener todas las fases del proceso
            fases = modelo.query.all()
            
            # Generar gráficos en formato base64
            graficos = generar_graficos_base64(fases)
            
            
            # Rutas de las imágenes
            imagenes = {
                "logo_base64": os.path.join('app', 'static', 'img', 'Mogus.png'),
                "boceto21_base64": os.path.join('app', 'static', 'img', 'BOCETO 2.1.jpg'),
                "boceto13_base64": os.path.join('app', 'static', 'img', 'BOCETO 1.3.jpg'),
                "boceto12_base64": os.path.join('app', 'static', 'img', 'BOCETO 1.2.jpg')
            }
            # Cargar imágenes en base64
            imagenes_base64 = {}
            
            for clave, ruta in imagenes.items():
                try:
                    with open(ruta, "rb") as imagen_archivo:
                        imagenes_base64[clave] = base64.b64encode(imagen_archivo.read()).decode('utf-8')
                except Exception as e:
                    print(f"Error al cargar {ruta}: {str(e)}")
                    imagenes_base64[clave] = ""  # En caso de error, dejarlo vacío
            
            # Asignar variables individuales si es necesario
            logo_base64 = imagenes_base64["logo_base64"]
            """try:
                
                with open(logo_path, "rb") as imagen_archivo:
                    logo_base64 = base64.b64encode(imagen_archivo.read()).decode('utf-8')
                with open(boceto_21, "rb") as imagen_archivo:
                    boceto21_base64 = base64.b64encode(imagen_archivo.read()).decode('utf-8')
                with open(boceto_13, "rb") as imagen_archivo:
                    boceto_13_base64 = base64.b64encode(imagen_archivo.read()).decode('utf-8')
                with open(boceto_12, "rb") as imagen_archivo:    
                    boceto_12_base64 = base64.b64encode(imagen_archivo.read()).decode('utf-8')
            except Exception as e:
                print(f"Error al cargar el logo: {str(e)}")
                # Continúa sin el logo si hay error"""
            
            # Obtener timestamp para el reporte
            timestamp = get_colombian_time().strftime('%Y%m%d_%H%M')
            
            # Renderizar la plantilla HTML con los datos y gráficos en base64
            html_content = render_template('reportes/reporte_pdf.html', 
                                            fases=fases,
                                            proceso=proceso,
                                            timestamp=timestamp,
                                            now=get_colombian_time(),
                                            graficos=graficos,
                                            logo_base64=logo_base64,
                                            imagenes_base64=imagenes_base64,
                                            es_base64=True)
            
            # Definir estilos CSS para el PDF con optimizaciones para evitar páginas en blanco
            css = CSS(string='''
                @page {
                    size: A4 landscape;
                    margin: 2cm;
                    @top-center {
                        content: "MOGUS - Reporte de Infraestructura Verde";
                        font-size: 9pt;
                    }
                    @bottom-right {
                        content: "Página " counter(page) " de " counter(pages);
                        font-size: 9pt;
                    }
                }
                
                body {
                    font-family: Arial, sans-serif;
                    font-size: 11pt;
                    line-height: 1.5;
                    margin: 0;
                    padding: 0;
                }
                
                .report-container {
                    width: 100%;
                    margin: 0;
                    padding: 0;
                }
                
                .header-logo {
                    display: flex;
                    align-items: center;
                    margin-bottom: 20px;
                }
                
                .logo-img {
                    height: 60px;
                    margin-right: 15px;
                }
                
                h1 {
                    color: #2E7D32;
                    font-size: 22pt;
                    margin-bottom: 10px;
                }
                
                h2 {
                    color: #388E3C;
                    font-size: 16pt;
                    margin-top: 18px;
                    margin-bottom: 12px;
                }
                
                .report-date {
                    color: #616161;
                    font-style: italic;
                    margin-bottom: 20px;
                }
                
                .resumen-seccion {
                    background-color: #F1F8E9;
                    padding: 12px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                
                .resumen-item {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 6px;
                    padding-bottom: 4px;
                    border-bottom: 1px solid #E8F5E9;
                }
                
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                    font-size: 10pt;
                }
                
                th, td {
                    border: 1px solid #BDBDBD;
                    padding: 6px 8px;
                    text-align: left;
                }
                
                th {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                }
                
                tr:nth-child(even) {
                    background-color: #F5F5F5;
                }
                
                .viabilidad-viable {
                    color: #2E7D32;
                    font-weight: bold;
                }
                
                .viabilidad-media {
                    color: #F57F17;
                    font-weight: bold;
                }
                
                .viabilidad-no-viable {
                    color: #C62828;
                    font-weight: bold;
                }
                
                .chart-container {
                    margin-bottom: 25px;
                    page-break-inside: avoid;
                }
                
                .chart-title {
                    font-weight: bold;
                    color: #388E3C;
                    margin-bottom: 8px;
                    text-align: center;
                }
                
                .chart-image {
                    width: 100%;
                    max-width: 850px;
                    height: auto;
                    display: block;
                    margin: 0 auto;
                    max-height: 450px;
                }
                
                .page-break {
                    page-break-before: always;
                    height: 0;
                    margin: 0;
                    padding: 0;
                }
                
                .footer {
                    margin-top: 25px;
                    border-top: 1px solid #BDBDBD;
                    padding-top: 8px;
                    font-size: 9pt;
                    color: #757575;
                    text-align: center;
                }
                
                div:empty {
                    display: none;
                }
            ''')
            
            # Crear un objeto BytesIO para almacenar el PDF en memoria
            pdf_bytes = io.BytesIO()
            
            # Generar el PDF directamente en memoria
            doc = HTML(string=html_content).write_pdf(
                pdf_bytes,
                stylesheets=[css]
            )
            
            # Verificar si hay páginas en blanco y eliminarlas usando PyPDF2
            from PyPDF2 import PdfReader, PdfWriter
            pdf_bytes.seek(0)
            reader = PdfReader(pdf_bytes)
            writer = PdfWriter()
            
            # Criterio para determinar si una página está en blanco (puedes ajustar según necesidad)
            def is_page_blank(page):
                # Extrae el texto de la página
                text = page.extract_text()
                # Si no hay texto o solo hay espacios en blanco, consideramos que la página está en blanco
                return not text or text.isspace()
            
            # Copiar solo las páginas que no están en blanco
            for i in range(len(reader.pages)):
                if not is_page_blank(reader.pages[i]):
                    writer.add_page(reader.pages[i])
            
            # Crear un nuevo BytesIO para el PDF limpio
            final_pdf = io.BytesIO()
            writer.write(final_pdf)
            final_pdf.seek(0)
            
            # Nombre del archivo para descarga
            filename = f"Reporte_{proceso}_{timestamp}.pdf"
            
            # Enviar el PDF optimizado
            return send_file(
                final_pdf,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f'Error al generar el PDF: {str(e)}', 'danger')
            return redirect(url_for(proceso))
        

    @app.route('/exportar_excel/<proceso>')
    @handle_errors
    def exportar_excel(proceso):
        modelo = get_model_by_process(proceso)
        
        if not modelo:
            flash('Proceso no válido para exportación', 'danger')
            return redirect(url_for('home'))
        
        try:
            # Función para calcular viabilidad
            def calcular_viabilidad(area_verde, area_total):
                porcentaje = (area_verde / area_total) if area_total > 0 else 0
                if porcentaje >= 0.7:
                    return "Viable ✅"
                elif porcentaje >= 0.4:
                    return "Medianamente viable ⚠️"
                else:
                    return "No viable ❌"

            # Obtener todas las fases del proceso
            fases = modelo.query.all()
            
            # Preparar los datos para el DataFrame
            data = []
            for fase in fases:
                # Calcular porcentaje del indicador como (Area Verde / Area Total) * 100
                porcentaje_calculado = (fase.area_verde / fase.area_total * 100) if fase.area_total > 0 else 0
                
                data.append({
                    'ID': fase.id_Fase,
                    'Nombre Fase': fase.nombre_fase,
                    'Tipo': fase.tipo_fase,
                    'Descripción': fase.descripcion,
                    'Indicador': fase.indicador,
                    'Revisor': fase.nombre_revisor,
                    'Area Verde': fase.area_verde,
                    'Area Total': fase.area_total,
                    'Porcentaje Del Indicador': porcentaje_calculado,
                    'Viabilidad': calcular_viabilidad(fase.area_verde, fase.area_total),
                    'Fecha de Actualización': fase.fecha_actualizacion.strftime('%Y-%m-%d %H:%M'),
                    'Fecha de Creación': fase.fecha_creacion.strftime('%Y-%m-%d %H:%M')
                })
            
            # Crear DataFrame con pandas
            df = pd.DataFrame(data)
            
            # Crear un objeto BytesIO para guardar el archivo Excel
            output = io.BytesIO()
            
            # Utilizar ExcelWriter para personalizar el archivo
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Escribir DataFrame a Excel
                df.to_excel(writer, sheet_name='Infraestructura Verde', index=False)
                
                # Obtener el objeto workbook y worksheet
                workbook = writer.book
                worksheet = writer.sheets['Infraestructura Verde']
                
                # Añadir formatos
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#4CAF50',
                    'font_color': 'white',
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1     
                })
                
                # Formato para números con porcentaje
                percent_format = workbook.add_format({
                    'num_format': '0.00%',
                    'align': 'center'
                })
                
                # Aplicar formato a los encabezados
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Añadir fórmula de cálculo de porcentaje
                # Añadir fórmula de cálculo de porcentaje
                for row in range(2, len(df) + 2):
                    # Fórmula para porcentaje
                    worksheet.write_formula(
                        f'I{row}', 
                        f'=G{row}/H{row}', 
                        percent_format
                    )
                    
                    # Añadir fórmula para calcular viabilidad
                    worksheet.write_formula(
                        f'J{row}', 
                        f'=IF(I{row}>=0.7, "Viable ✅", IF(I{row}>=0.4, "Medianamente viable ⚠️", "No viable ❌"))', 
                        workbook.add_format({
                            'align': 'center'
                        })
                    )
                
                # Ajustar el ancho de las columnas automáticamente
                for i, col in enumerate(df.columns):
                    max_len = max(
                        df[col].astype(str).map(len).max(),
                        len(col) + 2
                    )
                    worksheet.set_column(i, i, max_len)
                
                # Formato condicional para viabilidad
                worksheet.conditional_format('J2:J' + str(len(df) + 2), {
                    'type': 'text',
                    'criteria': 'containing',
                    'color': '#00FF00',  # Verde
                    'background_color': '#C6EFCE',
                    'value': 'Viable'
                })

                worksheet.conditional_format('J2:J' + str(len(df) + 1), {
                    'type': 'text',
                    'criteria': 'containing',
                    'color': '#FFC000',  # Amarillo
                    'background_color': '#FFEB9C',
                    'value': 'Medianamente viable'
                })

                worksheet.conditional_format('J2:J' + str(len(df) + 1), {
                    'type': 'text',
                    'criteria': 'containing',
                    'color': '#FF0000',  # Rojo
                    'background_color': '#FFC7CE',
                    'value': 'No viable'
                })
                
                # Configuración del pie de página
                worksheet.set_footer('&LExportado: &D &T&RInfraestructura Verde - MOGUS')
            
            # Preparar el archivo para descarga
            output.seek(0)
            
            # Generar nombre del archivo con fecha y hora
            timestamp = get_colombian_time().strftime('%Y%m%d_%H%M')
            filename = f"{proceso}_{timestamp}.xlsx"
            
            return send_file(
                output,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        except Exception as e:
            flash(f'Error al exportar a Excel: {str(e)}', 'danger')
            return redirect(url_for(proceso))


    @app.route('/descargar_excel/<proceso>')
    def descargar_excel(proceso):
        if proceso == 'Parque_Urbano':
            excel_path = os.path.join(app.static_folder, 'excel', 'INDICADORESPARQUESURBANOS.xlsx')
            return send_file(excel_path, as_attachment=True, download_name='Parque_Urbano.xlsx')
        elif proceso == 'Corredor_Urbano':
            excel_path = os.path.join(app.static_folder, 'excel', 'INDICADORESCORREDORESECOLOGICOS.xlsx')
            return send_file(excel_path, as_attachment=True, download_name='Corredor_Urbano.xlsx')
        else:
            return f"No se encontró archivo Excel para el proceso: {proceso}", 404

    import locale
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Para Linux/macOS
    # locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')  # Para Windows


    # Manejo de errores mejorado
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app
# Punto de entrada de la aplicación
if __name__ == '__main__':
    app = crear_app()  # Creamos la app usando la función crear_app
    with app.app_context():
        db.create_all()  # Crea las tablas en la base de datos
    app.run(port=5000, debug=True)  # Inicia la aplicación Flask en el puerto 5000 con modo debug activado

