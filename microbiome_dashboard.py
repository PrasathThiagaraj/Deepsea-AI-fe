#!/usr/bin/env python3
# =============================================================================
# 💡 IMPORTANT: To generate PDF reports, you need to install the 'reportlab' library.
# Run this command in your terminal:
# pip install reportlab
# =============================================================================

import os
import sys
import json
import base64
import random
import tempfile
from datetime import datetime
from io import BytesIO

import django
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

# --- PDF Generation Dependency ---
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# =============================================================================
# DJANGO CONFIGURATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

settings.configure(
    DEBUG=True,
    SECRET_KEY='microbiome-dashboard-prototype-key-2024',
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['*'],
    
    INSTALLED_APPS=[
        'django.contrib.staticfiles',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
    ],
    
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ],
    
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    }],
    
    STATIC_URL='/static/',
    STATIC_ROOT=os.path.join(BASE_DIR, 'staticfiles'),
    
    FILE_UPLOAD_MAX_MEMORY_SIZE=100 * 1024 * 1024,  # 100MB
    DATA_UPLOAD_MAX_MEMORY_SIZE=100 * 1024 * 1024,   # 100MB
    
    SESSION_ENGINE='django.contrib.sessions.backends.cache',
    SESSION_CACHE_ALIAS='default',
    
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
)

django.setup()

# =============================================================================
# DATA MODELS & SIMULATION
# =============================================================================

class MicrobiomeAnalyzer:
    """Simulates microbiome analysis with realistic data generation"""
    
    @staticmethod
    def generate_taxonomy_data():
        """Generate realistic taxonomy data for visualization"""
        taxa_data = [
            {'name': 'Bacteroidetes', 'abundance': random.randint(25, 40), 'color': '#22d3ee'}, # Cyan
            {'name': 'Firmicutes', 'abundance': random.randint(20, 35), 'color': '#f472b6'}, # Pink
            {'name': 'Proteobacteria', 'abundance': random.randint(10, 20), 'color': '#4ade80'}, # Green
            {'name': 'Actinobacteria', 'abundance': random.randint(5, 15), 'color': '#fb923c'}, # Orange
            {'name': 'Verrucomicrobia', 'abundance': random.randint(2, 8), 'color': '#a78bfa'}, # Violet
            {'name': 'Fusobacteria', 'abundance': random.randint(1, 5), 'color': '#34d399'}, # Emerald
            {'name': 'Spirochaetes', 'abundance': random.randint(1, 4), 'color': '#60a5fa'}, # Blue
            {'name': 'Other', 'abundance': random.randint(2, 8), 'color': '#94a3b8'},       # Slate
        ]
        total = sum(t['abundance'] for t in taxa_data)
        for taxa in taxa_data:
            taxa['abundance'] = round((taxa['abundance'] / total) * 100, 1)
        return taxa_data
    
    @staticmethod
    def generate_heatmap_data():
        """Generate abundance heatmap data"""
        samples = [f'Sample_{i+1}' for i in range(8)]
        taxa = ['Bacteroides', 'Lactobacillus', 'Bifidobacterium', 'E.coli', 'Clostridium', 'Akkermansia', 'Prevotella', 'Enterococcus']
        heatmap_data = []
        for taxon in taxa:
            row = {'taxon': taxon, 'values': [round(random.uniform(0.1, 10.0), 2) for _ in samples]}
            heatmap_data.append(row)
        return {'samples': samples, 'data': heatmap_data}

    @staticmethod
    def generate_novelty_data():
        """Generate AI-powered novelty detection results"""
        return [
            {'cluster_id': 'NC001', 'confidence': 0.92, 'similarity': 0.34, 'potential_species': 'Unknown Bacteroidetes sp.', 'abundance': 2.3, 'unique_features': ['Novel metabolic pathway', '16S rRNA variation']},
            {'cluster_id': 'NC002', 'confidence': 0.87, 'similarity': 0.41, 'potential_species': 'Unclassified Firmicutes', 'abundance': 1.8, 'unique_features': ['Antimicrobial resistance genes', 'Biofilm formation']},
            {'cluster_id': 'NC003', 'confidence': 0.79, 'similarity': 0.28, 'potential_species': 'Novel Actinobacteria', 'abundance': 0.9, 'unique_features': ['Secondary metabolite production', 'Extreme pH tolerance']}
        ]

# =============================================================================
# VIEWS
# =============================================================================

def dashboard_view(request):
    """Main dashboard view"""
    return HttpResponse(DASHBOARD_TEMPLATE)

@csrf_exempt
def upload_fastq(request):
    """Handle FASTQ file upload and initiate processing"""
    if request.method == 'POST' and request.FILES.get('fastq_file'):
        uploaded_file = request.FILES['fastq_file']
        if not uploaded_file.name.endswith(('.fastq', '.fq', '.fastq.gz', '.fq.gz')):
            return JsonResponse({'error': 'Please upload a valid FASTQ file'}, status=400)
        
        request.session['uploaded_file'] = {'name': uploaded_file.name, 'size': uploaded_file.size, 'upload_time': datetime.now().isoformat()}
        return JsonResponse({'success': True, 'file_name': uploaded_file.name, 'file_size': uploaded_file.size, 'processing_id': 'proc_' + str(random.randint(10000, 99999))})
    
    return JsonResponse({'error': 'No file uploaded'}, status=400)

def processing_status(request):
    """Simulate processing status updates"""
    processing_id = request.GET.get('id')
    steps = [
        {'name': 'Quality Control (QC)', 'status': 'completed', 'progress': 100},
        {'name': 'Adapter & Quality Trimming', 'status': 'completed', 'progress': 100},
        {'name': 'Taxonomic Classification', 'status': 'completed', 'progress': 100},
        {'name': 'Abundance Calculation', 'status': 'completed', 'progress': 100},
        {'name': 'AI Novelty Detection', 'status': 'completed', 'progress': 100},
        {'name': 'Generating Visualizations', 'status': 'completed', 'progress': 100},
    ]
    return JsonResponse({'processing_id': processing_id, 'overall_progress': 100, 'status': 'completed', 'steps': steps})

def get_taxonomy_data(request):
    """Return taxonomy chart data"""
    return JsonResponse({'taxonomy_data': MicrobiomeAnalyzer.generate_taxonomy_data()})

def get_heatmap_data(request):
    """Return abundance heatmap data"""
    return JsonResponse(MicrobiomeAnalyzer.generate_heatmap_data())

def get_novelty_data(request):
    """Return AI novelty detection results"""
    return JsonResponse({'novel_clusters': MicrobiomeAnalyzer.generate_novelty_data()})

def download_report(request):
    """Generate and download analysis report"""
    report_type = request.GET.get('type', 'pdf')
    
    if report_type == 'csv':
        taxonomy_data = MicrobiomeAnalyzer.generate_taxonomy_data()
        csv_content = "Sample,Taxon,Abundance\n" + "".join([f"Sample_1,{taxa['name']},{taxa['abundance']}\n" for taxa in taxonomy_data])
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="microbiome_analysis.csv"'
        return response
    
    else:
        if not REPORTLAB_AVAILABLE:
            error_msg = "PDF generation failed. Please install 'reportlab' via 'pip install reportlab'."
            return HttpResponse(error_msg, status=500, content_type="text/plain")

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=(8.5 * inch, 11 * inch))

        # --- Report Content ---
        p.setTitle("Microbiome Analysis Report")
        p.setFont("Helvetica-Bold", 18)
        p.drawCentredString(4.25 * inch, 10.5 * inch, "Microbiome Analysis Report")

        p.setFont("Helvetica", 10)
        p.drawString(inch, 10.2 * inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        p.line(inch, 10.1 * inch, 7.5 * inch, 10.1 * inch)

        # Summary Section
        p.setFont("Helvetica-Bold", 14)
        p.drawString(inch, 9.5 * inch, "Analysis Summary")
        p.setFont("Helvetica", 11)
        text = p.beginText(1.2 * inch, 9.2 * inch)
        text.textLines("""
            • Total taxa identified: 8
            • Novel clusters found: 3
            • Dominant phylum: Bacteroidetes
            • Sample diversity: High
        """)
        p.drawText(text)

        # AI Insights Section
        p.setFont("Helvetica-Bold", 14)
        p.drawString(inch, 8.2 * inch, "AI-Powered Insights")
        p.setFont("Helvetica", 11)
        text = p.beginText(1.2 * inch, 7.9 * inch)
        text.textLines("""
            • 3 potentially novel species detected with high confidence.
            • Unique metabolic pathways identified in novel clusters.
            • Antimicrobial resistance (AMR) genes present in cluster NC002.
        """)
        p.drawText(text)

        p.showPage()
        p.save()
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="microbiome_analysis.pdf"'
        return response

# =============================================================================
# URL CONFIGURATION
# =============================================================================

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('upload/', upload_fastq, name='upload_fastq'),
    path('processing_status/', processing_status, name='processing_status'),
    path('api/taxonomy/', get_taxonomy_data, name='taxonomy_data'),
    path('api/heatmap/', get_heatmap_data, name='heatmap_data'),
    path('api/novelty/', get_novelty_data, name='novelty_data'),
    path('download_report/', download_report, name='download_report'),
]

# =============================================================================
# HTML TEMPLATE (DEEP SEA THEME)
# =============================================================================

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DeepSea AI - Dashboard</title>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        /* =================================================================== */
        /* DEEP SEA / BIOLUMINESCENCE THEME */
        /* =================================================================== */
        :root {
            --primary-glow: #22d3ee; --primary-dark: #0891b2;
            --success-glow: #2dd4bf; --error-glow: #fb7185;
            
            --bg-dark: #e0f7fa;         /* light aqua background */
        --bg-darker: #f0fdfd;       /* very light aqua (almost white) */
        --surface-color: rgba(255, 255, 255, 0.8); /* frosted white panels */
--border-color: rgba(0, 150, 199, 0.2);    /* soft aqua borders */

--text-light: #0f172a;      /* dark text */
--text-lighter: #1e293b;    /* slightly lighter dark */
--text-dark: #475569;   
            
            --sidebar-width: 260px;
            --shadow-glow: 0 0 20px 0 rgba(34, 211, 238, 0.2);
            --radius-md: 0.5rem; --radius-lg: 0.75rem; --radius-xl: 1rem;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background-color: var(--bg-darker); background-image: linear-gradient(180deg, var(--bg-darker) 0%, var(--bg-dark) 100%); color: var(--text-light); line-height: 1.6; }
        
        /* Layout */
        .dashboard-container { display: flex; min-height: 100vh; }
        .sidebar { width: var(--sidebar-width); background-color: var(--surface-color); border-right: 1px solid var(--border-color); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); padding: 1.5rem 0; position: fixed; height: 100vh; z-index: 100; transition: transform 0.3s ease; }
        .main-content { flex: 1; margin-left: var(--sidebar-width); padding: 2rem; max-width: 1600px; }
        .content-wrapper { max-width: 1200px; margin: 0 auto; }
        .page-section { background-color: var(--surface-color); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-radius: var(--radius-xl); padding: 2rem; margin-bottom: 2rem; border: 1px solid var(--border-color); animation: fadeIn 0.5s ease forwards; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        /* Sidebar */
        .logo { padding: 0 1.5rem 1.5rem; border-bottom: 1px solid var(--border-color); margin-bottom: 1.5rem; }
        .logo h1 { font-size: 1.5rem; font-weight: 700; color: var(--primary-glow); display: flex; align-items: center; gap: 0.75rem; }
        .logo-icon { font-size: 1.75rem; }
        .nav-menu { list-style: none; padding: 0 1rem; }
        .nav-link { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; color: var(--text-dark); text-decoration: none; border-radius: var(--radius-md); transition: all 0.2s ease; font-weight: 500; }
        .nav-link:hover { color: var(--text-lighter); background-color: rgba(34, 211, 238, 0.1); }
        .nav-link.active { color: var(--primary-glow); background-color: rgba(34, 211, 238, 0.1); font-weight: 600; }
        .nav-icon { width: 20px; height: 20px; }
        
        /* Header */
        .header h1 { font-size: 2rem; font-weight: 700; color: var(--text-lighter); margin-bottom: 0.25rem; }
        .header p { color: var(--text-dark); font-size: 1rem; }
        
        /* Upload Section */
        .upload-zone { border: 2px dashed var(--border-color); border-radius: var(--radius-lg); padding: 3rem; text-align: center; background-color: rgba(0,0,0,0.1); transition: all 0.3s ease; cursor: pointer; }
        .upload-zone:hover, .upload-zone.dragover { border-color: var(--primary-glow); background-color: rgba(34, 211, 238, 0.1); box-shadow: var(--shadow-glow); }
        .upload-icon { font-size: 2.5rem; color: var(--primary-glow); margin-bottom: 1rem; }
        .upload-text h3 { font-size: 1.25rem; color: var(--text-lighter); margin-bottom: 0.5rem; }
        .file-input { display: none; }
        
        /* Processing Stepper */
        .processing-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; }
        .processing-spinner { width: 32px; height: 32px; border: 4px solid var(--border-color); border-top: 4px solid var(--primary-glow); border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .stepper { position: relative; }
        .step { display: flex; align-items: flex-start; gap: 1rem; position: relative; padding-bottom: 2rem; }
        .step:not(:last-child)::before { content: ''; position: absolute; left: 16px; top: 32px; width: 2px; height: calc(100% - 1rem); background: var(--border-color); }
        .step.completed:not(:last-child)::before { background: var(--success-glow); }
        .step-icon-wrapper { z-index: 1; }
        .step-icon { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; color: var(--bg-darker); transition: all 0.3s ease; }
        .step-icon.pending { background: var(--text-dark); }
        .step-icon.active { background: var(--primary-glow); animation: pulse 1.5s infinite; color: var(--bg-darker); }
        .step-icon.completed { background: var(--success-glow); color: var(--bg-darker); }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(34, 211, 238, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(34, 211, 238, 0); } 100% { box-shadow: 0 0 0 0 rgba(34, 211, 238, 0); } }
        .step-content .step-title { font-weight: 600; color: var(--text-lighter); }
        .step-content .step-status { font-size: 0.875rem; color: var(--text-dark); }
        
        /* Tabs */
        .tabs-header { display: flex; border-bottom: 1px solid var(--border-color); margin-bottom: 2rem; }
        .tab-button { flex: 0; padding: 0.75rem 1.5rem; background: none; border: none; font-size: 1rem; font-weight: 500; color: var(--text-dark); cursor: pointer; transition: all 0.2s ease; border-bottom: 2px solid transparent; }
        .tab-button:hover { color: var(--primary-glow); }
        .tab-button.active { color: var(--primary-glow); border-bottom-color: var(--primary-glow); }
        .tab-content { display: none; }
        .tab-content.active { display: block; animation: fadeIn 0.4s; }
        .chart-container { position: relative; height: 400px; margin-bottom: 2rem; }
        .section-title { font-size: 1.5rem; font-weight: 600; color: var(--text-lighter); margin-bottom: 1.5rem; }
        
        /* AI Novelty Cards */
        #novelClustersContainer { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; }
        .novel-cluster { background-color: var(--bg-dark); border-radius: var(--radius-lg); padding: 1.5rem; border: 1px solid var(--border-color); border-left: 4px solid var(--primary-glow); transition: all 0.3s ease; }
        .novel-cluster:hover { transform: translateY(-4px); box-shadow: var(--shadow-glow); border-color: var(--primary-glow); }
        .confidence-badge { background-color: rgba(45, 212, 191, 0.1); color: var(--success-glow); padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.8rem; font-weight: 600; }
        .cluster-species { font-weight: 600; font-size: 1.1rem; color: var(--text-lighter); margin: 0.5rem 0; }
        .feature-tag { background-color: rgba(34, 211, 238, 0.1); color: var(--primary-glow); padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.8rem; font-weight: 500; }
        
        /* Buttons & Controls */
        .btn { display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; padding: 0.65rem 1.25rem; border: 1px solid transparent; border-radius: var(--radius-md); font-size: 0.875rem; font-weight: 600; cursor: pointer; transition: all 0.2s ease; text-decoration: none; }
        .btn-primary { background: var(--primary-glow); color: var(--bg-darker); box-shadow: 0 0 15px 0 rgba(34, 211, 238, 0.4); }
        .btn-primary:hover { background: var(--primary-dark); color: var(--text-lighter); box-shadow: 0 0 25px 0 rgba(34, 211, 238, 0.6); transform: translateY(-2px); }
        .btn-secondary { background: transparent; color: var(--text-light); border-color: var(--border-color); }
        .btn-secondary:hover { background: var(--border-color); color: var(--text-lighter); }
        
        /* Messages */
        .message-box { padding: 1rem; border-radius: var(--radius-md); margin-bottom: 1.5rem; border: 1px solid; display: none; font-weight: 500; backdrop-filter: blur(10px); }
        .success-message { background-color: rgba(45, 212, 191, 0.1); border-color: rgba(45, 212, 191, 0.5); color: var(--success-glow); }
        .error-message { background-color: rgba(251, 113, 133, 0.1); border-color: rgba(251, 113, 133, 0.5); color: var(--error-glow); }
        .novel-cluster .cluster-id,
        .novel-cluster .feature-tag, .confidence-badge {
            color: rgba(0, 100, 0, 1) !important;
        }
        /* Cluster ID (e.g., NC002) */
.novel-cluster .cluster-id {
    font-size: 1.6rem;    /* larger for slides */
    font-weight: 800;     /* extra bold */
    letter-spacing: 0.6px;
    display: block;       /* ensures spacing */
    margin-bottom: 0.5rem;
}

/* Feature tags (e.g., Antimicrobial resistance genes, Biofilm formation) */
.novel-cluster .feature-tag {
    font-size: 1.1rem;     /* bigger text */
    font-weight: 600;
    padding: 0.5rem 1.2rem;
    border-radius: 12px;
    margin: 0.3rem 0.3rem 0 0; /* spacing between badges */
    display: inline-block;
}

/* Confidence badge (e.g., 87% Confidence) */
.novel-cluster .confidence-badge {
    font-size: 1rem;       /* slightly larger */
    font-weight: 700;      /* bold */
    padding: 0.4rem 1rem;
    border-radius: 12px;
    display: inline-block;
    margin-bottom: 0.8rem;
}

        /* Responsive Design */
        .menu-toggle { display: none; }
        @media (max-width: 1024px) {
            .sidebar { transform: translateX(-100%); }
            .sidebar.open { transform: translateX(0); box-shadow: 0 0 40px rgba(0,0,0,0.5); }
            .main-content { margin-left: 0; }
            .menu-toggle { display: block; position: fixed; top: 1.5rem; left: 1.5rem; z-index: 101; background: var(--surface-color); backdrop-filter: blur(10px); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 0.5rem; cursor: pointer; }
            .menu-toggle-icon { width: 24px; height: 24px; color: var(--text-light); }
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <aside class="sidebar" id="sidebar">
            <div class="logo"><h1><span class="logo-icon">⚓️</span>DeepSea AI</h1></div>
            <nav>
                <ul class="nav-menu">
                    <li><a href="#" class="nav-link active" data-section="uploadSection"><svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>Upload Sample</a></li>
                    <li><a href="#" class="nav-link" data-section="processingSection"><svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>Processing</a></li>
                    <li><a href="#" class="nav-link" data-section="resultsSection"><svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>Results</a></li>
                    <li><a href="#" class="nav-link" data-section="downloadSection"><svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>Download Reports</a></li>
                </ul>
            </nav>
        </aside>
        
        <main class="main-content">
            <button class="menu-toggle" id="menuToggle">
                <svg class="menu-toggle-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            </button>
            <div class="content-wrapper">
                <header class="header page-section">
                    <h1>Deep Dive Analysis</h1>
                    <p>AI-powered microbiome sequencing from the abyssal depths of your data.</p>
                </header>
                
                <div id="successMessage" class="message-box success-message"></div>
                <div id="errorMessage" class="message-box error-message"></div>
                
                <section id="uploadSection" class="page-section">
                    <h2 class="section-title">1. Deploy Your Sample</h2>
                    <div class="upload-zone" id="uploadZone">
                        <div class="upload-icon">⚓</div>
                        <div class="upload-text">
                            <h3>Drop your FASTQ file into the trench</h3>
                            <p>or click to browse local databanks</p>
                        </div>
                        <input type="file" id="fileInput" class="file-input" accept=".fastq,.fq,.fastq.gz,.fq.gz">
                    </div>
                </section>
                
                <section id="processingSection" class="page-section" style="display: none;">
                    <div class="processing-header">
                        <div class="processing-spinner"></div>
                        <div>
                            <h2 class="section-title" style="margin-bottom:0;">2. Sonar Scan in Progress</h2>
                            <p>Our AI is analyzing your sample. This may take a few moments...</p>
                        </div>
                    </div>
                    <div class="stepper" id="processingSteps"></div>
                </section>
                
                <section id="resultsSection" class="page-section" style="display: none;">
                    <h2 class="section-title">3. Analysis Results</h2>
                    <div class="tabs-header">
                        <button class="tab-button active" data-tab="taxonomy">Taxonomy</button>
                        <button class="tab-button" data-tab="abundance">Abundance Heatmap</button>
                        <button class="tab-button" data-tab="novelty">AI Novelty Detection</button>
                    </div>
                    <div id="taxonomyTab" class="tab-content active"><div class="chart-container"><canvas id="taxonomyChart"></canvas></div><div class="chart-container"><canvas id="taxonomyBarChart"></canvas></div></div>
                    <div id="abundanceTab" class="tab-content"><div id="heatmapContainer" style="overflow-x: auto;"></div></div>
                    <div id="noveltyTab" class="tab-content"><div id="novelClustersContainer"></div></div>
                </section>
                
                <section id="downloadSection" class="page-section">
                    <h2 class="section-title">4. Surface the Data</h2>
                    <p style="margin-bottom: 1.5rem;">Export your complete microbiome analysis for publication or further research.</p>
                    <div class="download-buttons">
                        <a href="/download_report/?type=pdf" class="btn btn-primary" target="_blank">Download PDF Report</a>
                        <a href="/download_report/?type=csv" class="btn btn-secondary" target="_blank">Download CSV Data</a>
                        <button class="btn btn-secondary" onclick="downloadCharts()">Download Charts as PNG</button>
                    </div>
                </section>
            </div>
        </main>
    </div>
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        let taxonomyPieChart = null, taxonomyBarChart = null;

        const sidebar = document.getElementById('sidebar');
        const menuToggle = document.getElementById('menuToggle');
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');
        
        menuToggle.addEventListener('click', () => sidebar.classList.toggle('open'));
        
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                document.getElementById(e.currentTarget.dataset.section)?.scrollIntoView({ behavior: 'smooth' });
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                e.currentTarget.classList.add('active');
                if (window.innerWidth <= 1024) sidebar.classList.remove('open');
            });
        });
        
        uploadZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => e.target.files[0] && uploadFile(e.target.files[0]));
        ['dragover', 'dragleave', 'drop'].forEach(ev => uploadZone.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); }));
        ['dragenter', 'dragover'].forEach(ev => uploadZone.addEventListener(ev, () => uploadZone.classList.add('dragover')));
        ['dragleave', 'drop'].forEach(ev => uploadZone.addEventListener(ev, () => uploadZone.classList.remove('dragover')));
        uploadZone.addEventListener('drop', (e) => e.dataTransfer.files[0] && uploadFile(e.dataTransfer.files[0]));

        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', e => {
                const targetTab = e.currentTarget.dataset.tab;
                document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                e.currentTarget.classList.add('active');
                document.getElementById(targetTab + 'Tab').classList.add('active');
            });
        });

        function showMessage(type, message) {
            const el = document.getElementById(type + 'Message');
            el.textContent = message;
            el.style.display = 'block';
            setTimeout(() => el.style.display = 'none', 5000);
        }
        
        async function uploadFile(file) {
            const formData = new FormData();
            formData.append('fastq_file', file);
            showMessage('success', `Uploading "${file.name}"...`);
            try {
                const response = await fetch('/upload/', { method: 'POST', body: formData });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Upload failed');
                showMessage('success', `File "${data.file_name}" uploaded! Starting analysis...`);
                startProcessing(data.processing_id);
            } catch (error) { showMessage('error', error.message); }
        }

        function startProcessing(processingId) {
            const section = document.getElementById('processingSection');
            section.style.display = 'block';
            section.scrollIntoView({ behavior: 'smooth' });
            const interval = setInterval(async () => {
                try {
                    const response = await fetch(`/processing_status/?id=${processingId}`);
                    const data = await response.json();
                    updateProcessingUI(data.steps);
                    if (data.status === 'completed') { clearInterval(interval); processingComplete(); }
                } catch (error) { clearInterval(interval); showMessage('error', 'Failed to get processing status.'); }
            }, 1000);
            updateProcessingUI([]);
        }
        
        function updateProcessingUI(steps) {
            const container = document.getElementById('processingSteps');
            container.innerHTML = steps.map((step, index) => `<div class="step ${step.status}"><div class="step-icon-wrapper"><div class="step-icon ${step.status}">${step.status === 'completed' ? '✓' : index + 1}</div></div><div class="step-content"><div class="step-title">${step.name}</div><div class="step-status">${step.status === 'completed' ? 'Completed' : 'Pending'}</div></div></div>`).join('');
        }

        function processingComplete() {
            showMessage('success', 'Analysis complete! Results are now available.');
            const section = document.getElementById('resultsSection');
            section.style.display = 'block';
            section.scrollIntoView({ behavior: 'smooth' });
            loadAllResults();
        }

        async function loadAllResults() {
            try {
                const [tax, heat, novel] = await Promise.all([ fetch('/api/taxonomy/').then(r => r.json()), fetch('/api/heatmap/').then(r => r.json()), fetch('/api/novelty/').then(r => r.json()) ]);
                renderTaxonomyCharts(tax.taxonomy_data);
                renderHeatmap(heat);
                renderNoveltyResults(novel.novel_clusters);
            } catch (error) { showMessage('error', 'Failed to load analysis results.'); }
        }

        function renderTaxonomyCharts(data) {
            const chartTextColor = '#000000';
            const chartGridColor = 'rgba(50, 75, 110, 0.5)';
            const commonOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: chartTextColor, font: { size: 14 } } }, title: { display: true, color: chartTextColor, font: { size: 16 } } } };
            
            const pieCtx = document.getElementById('taxonomyChart').getContext('2d');
            const barCtx = document.getElementById('taxonomyBarChart').getContext('2d');
            const labels = data.map(d => d.name);
            const abundances = data.map(d => d.abundance);
            const colors = data.map(d => d.color);

            if (taxonomyPieChart) taxonomyPieChart.destroy();
            taxonomyPieChart = new Chart(pieCtx, { type: 'doughnut', data: { labels, datasets: [{ data: abundances, backgroundColor: colors, borderWidth: 2, borderColor: '#0f172a' }] }, options: { ...commonOptions, plugins: {...commonOptions.plugins, title: { ...commonOptions.plugins.title, text: 'Taxonomic Composition (Phylum)'}} } });
            
            if (taxonomyBarChart) taxonomyBarChart.destroy();
            taxonomyBarChart = new Chart(barCtx, { type: 'bar', data: { labels, datasets: [{ label: 'Relative Abundance (%)', data: abundances, backgroundColor: colors.map(c => c + 'B3'), borderColor: colors, borderWidth: 1 }] }, options: { ...commonOptions, plugins: { legend: { display: false }, title: { ...commonOptions.plugins.title, text: 'Relative Abundance of Taxa' } }, scales: { y: { beginAtZero: true, ticks: { color: chartTextColor }, grid: { color: chartGridColor } }, x: { ticks: { color: chartTextColor }, grid: { color: 'transparent' } } } } });
        }
        
        function renderHeatmap({ samples, data }) {
            const container = document.getElementById('heatmapContainer');
            const table = document.createElement('table');
            table.style.cssText = 'width: 100%; border-collapse: collapse;';
            let html = `<thead><tr style="background-color:rgba(0,0,0,0.2);"><th style="padding:0.75rem; text-align:left;">Taxon</th>${samples.map(s => `<th>${s}</th>`).join('')}</tr></thead><tbody>`;
            const colorScale = (val, max) => `rgba(34, 211, 238, ${Math.min(val / max, 1)})`;
            data.forEach(row => {
                html += `<tr><td style="padding:0.5rem 0.75rem; font-weight:600; text-align:left; border-top:1px solid var(--border-color);">${row.taxon}</td>`;
                row.values.forEach(val => {
                    const bgColor = colorScale(val, 10);
                    html += `<td style="background-color:${bgColor}; color: '#000000'}; text-align:center; padding: 0.5rem; border-top:1px solid var(--border-color);">${val}</td>`;
                });
                html += `</tr>`;
            });
            table.innerHTML = html + '</tbody>';
            container.innerHTML = '';
            container.appendChild(table);
        }

        function renderNoveltyResults(clusters) {
            const container = document.getElementById('novelClustersContainer');
            container.innerHTML = clusters.map(c => `<div class="novel-cluster"><div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem;"><div class="feature-tag" style="font-family:monospace;">${c.cluster_id}</div><div class="confidence-badge">${Math.round(c.confidence * 100)}% Confidence</div></div><h4 class="cluster-species">${c.potential_species}</h4><div style="display:flex; justify-content:space-between; gap:1rem; margin-bottom:1rem; font-size:0.875rem;"><div class="detail-item"><span style="color:var(--text-dark);">Similarity</span><br><span style="font-weight:600; color:var(--text-lighter);">${(c.similarity * 100).toFixed(1)}%</span></div><div><span style="color:var(--text-dark);">Abundance</span><br><span style="font-weight:600; color:var(--text-lighter);">${c.abundance}%</span></div></div><div style="display:flex; flex-wrap:wrap; gap:0.5rem; margin-top:1rem;">${c.unique_features.map(f => `<span class="feature-tag">${f}</span>`).join('')}</div></div>`).join('');
        }
        
        window.downloadCharts = () => {
            const download = (canvas, filename) => { if (canvas) { const a = document.createElement('a'); a.download = filename; a.href = canvas.toDataURL('image/png'); a.click(); } };
            download(taxonomyPieChart?.canvas, 'taxonomy_composition.png');
            setTimeout(() => download(taxonomyBarChart?.canvas, 'taxonomy_abundance.png'), 500);
            showMessage('success', 'Downloading charts...');
        };
    });
    </script>
</body>
</html>
'''

# =============================================================================
# DJANGO APPLICATION RUNNER
# =============================================================================

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    
    if len(sys.argv) == 1:
        sys.argv = [__file__, 'runserver', '0.0.0.0:8000']
    
    if 'runserver' in sys.argv:
        print("\n" + "="*60)
        print("🦑 ABYSS ANALYTICS - DEEP DIVE DASHBOARD")
        print("="*60)
        print("🎨 UI Theme: Deep Sea / Bioluminescence")
        print("✅ PDF Generation: FIXED")
        print("📱 Responsiveness: ENABLED")
        print(f"\nStarting server at: http://localhost:{sys.argv[-1].split(':')[-1] or 8000}")
        if not REPORTLAB_AVAILABLE:
            print("\n⚠️ WARNING: 'reportlab' is not installed. PDF downloads will fail.")
            print("   Please install it using: pip install reportlab")
        print("="*60 + "\n")
        
    execute_from_command_line(sys.argv)