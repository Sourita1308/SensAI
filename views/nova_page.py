"""
views/nova_page.py
SensAI — Nova AI Accessibility Assistant Page
Renders the exact full-screen Tailwind CSS HTML design requested for Nova AI.
"""

import streamlit as st
import streamlit.components.v1 as components
from views.logo_data import LOGO_DARK_B64


def _css() -> str:
    return """
    <style>
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important; display: none !important;}
        header {visibility: hidden !important; display: none !important;}
        header[data-testid="stHeader"] {display: none !important;}
        section[data-testid="stSidebar"] {display: none !important;}
        button[data-testid="collapsedControl"] {display: none !important;}
        div[data-testid="stDecoration"] {display: none !important;}
        .block-container {
            padding: 0rem !important;
            margin: 0rem !important;
            max-width: 100% !important;
            width: 100% !important;
        }
        body, .stApp {
            background: #0f131c !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow-x: hidden !important;
        }
        iframe {
            border: none !important;
            width: 100% !important;
            display: block !important;
            margin: 0 !important;
            padding: 0 !important;
        }
    </style>
    """


def _get_nova_html() -> str:
    raw_html = """<!DOCTYPE html><html class="dark" lang="en"><head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<title>SensAI | Nova — Your Intelligent Accessibility Companion</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&amp;family=Inter:wght@300;400;500;600;700&amp;family=Fira+Code:wght@400;500&amp;display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet">
<script id="tailwind-config">
      tailwind.config = {
        darkMode: "class",
        theme: {
          extend: {
            "colors": {
                    "glass-bg": "rgba(13, 19, 32, 0.7)",
                    "on-tertiary-container": "#004e35",
                    "surface-container-lowest": "#0a0e17",
                    "surface-container": "#1c2029",
                    "on-background": "#dfe2ef",
                    "surface": "#0f131c",
                    "nova-gradient-mid": "#8ed5ff",
                    "surface-tint": "#7bd0ff",
                    "surface-dim": "#0f131c",
                    "outline-variant": "#3e484f",
                    "secondary-fixed-dim": "#bdc2ff",
                    "tertiary-fixed-dim": "#45dfa4",
                    "on-secondary-fixed": "#000767",
                    "error": "#ffb4ab",
                    "surface-container-high": "#262a34",
                    "surface-variant": "#31353f",
                    "on-secondary-container": "#a8afff",
                    "inverse-surface": "#dfe2ef",
                    "on-secondary-fixed-variant": "#2f3aa3",
                    "on-primary": "#00354a",
                    "primary-container": "#38bdf8",
                    "on-tertiary-fixed": "#002114",
                    "surface-container-highest": "#31353f",
                    "on-primary-container": "#004965",
                    "nova-gradient-end": "#34d399",
                    "primary": "#8ed5ff",
                    "nova-gradient-start": "#38bdf8",
                    "inverse-on-surface": "#2c303a",
                    "background": "#0f131c",
                    "tertiary": "#4ee6aa",
                    "on-error": "#690005",
                    "secondary": "#bdc2ff",
                    "surface-container-low": "#181b25",
                    "surface-bright": "#353943",
                    "on-tertiary-fixed-variant": "#005137",
                    "on-surface-variant": "#bdc8d1",
                    "tertiary-fixed": "#68fcbf",
                    "error-container": "#93000a",
                    "primary-fixed-dim": "#7bd0ff",
                    "inverse-primary": "#00668a",
                    "tertiary-container": "#22c990",
                    "glass-border": "rgba(30, 45, 69, 1)",
                    "secondary-container": "#2f3aa3",
                    "on-error-container": "#ffdad6",
                    "on-primary-fixed-variant": "#004c69",
                    "outline": "#87929a",
                    "primary-fixed": "#c4e7ff",
                    "secondary-fixed": "#e0e0ff",
                    "on-primary-fixed": "#001e2c",
                    "on-surface": "#dfe2ef",
                    "on-tertiary": "#003825",
                    "on-secondary": "#131e8c"
            },
            "borderRadius": {
                    "DEFAULT": "0.25rem",
                    "lg": "0.5rem",
                    "xl": "0.75rem",
                    "full": "9999px"
            },
            "spacing": {
                    "xl": "32px",
                    "container-max": "1280px",
                    "lg": "24px",
                    "xs": "4px",
                    "sm": "8px",
                    "md": "16px",
                    "margin": "24px",
                    "unit": "4px",
                    "gutter": "16px"
            },
            "fontFamily": {
                    "label-md": ["Inter"],
                    "code-md": ["Fira Code"],
                    "headline-lg": ["Inter"],
                    "headline-md": ["Inter"],
                    "body-sm": ["Inter"],
                    "body-md": ["Inter"],
                    "body-lg": ["Inter"],
                    "display-lg-mobile": ["Space Grotesk"],
                    "display-lg": ["Space Grotesk"]
            },
            "fontSize": {
                    "label-md": ["12px", {"lineHeight": "1", "letterSpacing": "0.05em", "fontWeight": "600"}],
                    "code-md": ["14px", {"lineHeight": "1.5", "fontWeight": "400"}],
                    "headline-lg": ["30px", {"lineHeight": "1.3", "fontWeight": "700"}],
                    "headline-md": ["24px", {"lineHeight": "1.3", "fontWeight": "700"}],
                    "body-sm": ["14px", {"lineHeight": "1.5", "fontWeight": "400"}],
                    "body-md": ["16px", {"lineHeight": "1.6", "fontWeight": "400"}],
                    "body-lg": ["18px", {"lineHeight": "1.6", "fontWeight": "400"}],
                    "display-lg-mobile": ["36px", {"lineHeight": "1.2", "fontWeight": "800"}],
                    "display-lg": ["48px", {"lineHeight": "1.1", "letterSpacing": "-0.02em", "fontWeight": "800"}]
            }
          },
        },
      }
    </script>
<style>
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        .float-animation { animation: float 4s ease-in-out infinite; }
        
        .glass-card {
            background: rgba(13, 19, 32, 0.6);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .glass-card:hover {
            background: rgba(13, 19, 32, 0.8);
            border-color: rgba(56, 189, 248, 0.4);
            transform: translateY(-4px);
            box-shadow: 0 10px 40px -10px rgba(56, 189, 248, 0.2);
        }

        .cta-press:active {
            transform: scale(0.95);
            transition: transform 0.1s;
        }

        .pulse-live {
            box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(52, 211, 153, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
        }

        .scroll-mask {
            mask-image: linear-gradient(to bottom, transparent, black 15%, black 85%, transparent);
        }

        .dropdown { position: relative; display: inline-block; }
        .dropdown-menu {
            display: none; position: absolute; top: 100%; left: 0;
            background: rgba(13, 19, 32, 0.95);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 0.75rem; padding: 0.5rem 0; min-width: 220px;
            z-index: 1000; box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }
        .dropdown.open .dropdown-menu { display: block; }
        .dd-item {
            padding: 0.75rem 1.25rem; font-size: 0.95rem; color: #dfe2ef;
            cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 0.75rem;
        }
        .dd-item:hover { background: rgba(56, 189, 248, 0.15); color: #8ed5ff; }
        .dd-icon { font-size: 1.25rem; }
    </style>
</head>
<body class="bg-surface text-on-surface font-body-md overflow-x-hidden">
<!-- TopNavBar Anchor -->
<nav class="fixed top-0 w-full z-50 bg-[#111127] shadow-[0_0_48px_rgba(182,160,255,0.08)]">
<div class="flex justify-between items-center max-w-7xl mx-auto px-8 h-20">
<div class="flex items-center gap-3" onclick="nav('home')" style="cursor:pointer;" title="SensAI Home">
<img alt="Nova Logo" class="h-10 w-10" src="LOGO_DARK_PLACEHOLDER">
<span class="text-2xl font-bold tracking-tighter text-[#e5e3ff] font-['Space_Grotesk']">SensAI</span>
</div>
<div class="hidden md:flex items-center gap-8 font-['Space_Grotesk'] tracking-tight"><a class="text-primary border-b-2 border-primary pb-1" onclick="nav('home')" style="cursor:pointer;" title="Home">Home</a><a class="text-[#e5e3ff]/70 hover:text-[#e5e3ff] transition-colors" onclick="nav('home')" style="cursor:pointer;" title="Features">Features</a><div class="dropdown" id="aiDD"><div class="flex items-center gap-1 text-[#e5e3ff]/70 hover:text-[#e5e3ff] cursor-pointer transition-colors" onclick="toggleDD()" style="cursor:pointer;" title="AI Modes"><span class="">AI Modes</span><span class="material-symbols-outlined text-sm">arrow_drop_down</span></div><div class="dropdown-menu"><div class="dd-item" onclick="nav('sign_language')" style="cursor:pointer;" title="Sign Language Mode"><span class="dd-icon">&#129335;</span>Sign Language</div><div class="dd-item" onclick="nav('ocr')" style="cursor:pointer;" title="OCR &amp; TTS Mode"><span class="dd-icon">&#128214;</span>OCR &amp; TTS</div><div class="dd-item" onclick="nav('emotion')" style="cursor:pointer;" title="Emotion Detection Mode"><span class="dd-icon">&#128522;</span>Emotion Detection</div><div class="dd-item" onclick="nav('scene')" style="cursor:pointer;" title="Scene Description Mode"><span class="dd-icon">&#127757;</span>Scene Description</div></div></div><a class="text-[#e5e3ff]/70 hover:text-[#e5e3ff] transition-colors" onclick="openModal('about')" style="cursor:pointer;" title="About">About</a><a class="text-[#e5e3ff]/70 hover:text-[#e5e3ff] transition-colors" onclick="openModal('contact')" style="cursor:pointer;" title="Contact">Contact</a></div>

</div>
</nav>
<!-- Hero Section -->
<section class="relative pt-32 pb-20 px-8 overflow-hidden">
<!-- Background Animation Placeholder -->
<div class="max-w-7xl mx-auto relative z-10 text-center flex flex-col items-center">
<div class="inline-flex items-center gap-2 bg-surface-container-low px-4 py-2 rounded-full mb-8 border border-outline-variant/30">
<span class="h-2 w-2 rounded-full bg-nova-gradient-end pulse-live"></span>
<span class="text-label-md font-label-md text-nova-gradient-end uppercase tracking-widest">Context-Aware AI Live</span>
</div>
<h1 class="font-display-lg text-display-lg-mobile md:text-display-lg text-on-background mb-6 max-w-4xl">
                Nova — Your <span class="bg-gradient-to-r from-primary to-nova-gradient-end bg-clip-text text-transparent">Intelligent Accessibility</span> Companion
            </h1>
<p class="text-body-lg text-on-surface-variant max-w-2xl mb-10">
                Empowering every user with technical precision and real-time sensory augmentation. Nova transforms the world into a structured, accessible digital layer.
            </p>
<div class="flex flex-col sm:flex-row gap-4">
<button class="px-8 py-4 bg-primary text-on-primary rounded-xl font-label-md text-label-md flex items-center gap-2 hover:shadow-[0_0_30px_rgba(56,189,248,0.4)] transition-all cta-press" onclick="document.getElementById('chat-studio').scrollIntoView({behavior:'smooth'});">
<span class="material-symbols-outlined">rocket_launch</span>
                    Launch Nova Assistant
                </button>
<button class="px-8 py-4 border border-outline-variant rounded-xl font-label-md text-label-md text-on-surface hover:bg-surface-variant transition-all cta-press" onclick="nav('ocr');">
                    Explore API
                </button>
</div><div class="mt-16 w-full max-w-4xl mx-auto flex flex-col gap-6"><!-- Neural Chat Studio -->
<div class="bg-primary-container/10 rounded-[2rem] p-8 flex items-center gap-6 shadow-xl hover:shadow-2xl transition-all cursor-pointer group" onclick="document.getElementById('chat-studio').scrollIntoView({behavior:'smooth'});">
<div class="h-16 w-16 rounded-full bg-[#2563eb] flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/20">
<span class="material-symbols-outlined text-white text-3xl">chat</span>
</div>
<div class="flex-1 text-left">
<h3 class="text-2xl font-bold text-on-surface mb-1">Neural Chat Studio</h3>
<p class="text-on-surface-variant text-body-md">Experience human-like conversations with machine precision and semantic intent.</p>
</div>
<div class="h-12 w-12 rounded-full bg-surface-container flex items-center justify-center text-slate-400 group-hover:bg-primary group-hover:text-on-primary transition-colors">
<span class="material-symbols-outlined">arrow_forward</span>
</div>
</div>
<!-- Interactive Walkthroughs -->
<div class="bg-primary-container/10 rounded-[2rem] p-8 flex items-center gap-6 shadow-xl hover:shadow-2xl transition-all cursor-pointer group" onclick="document.getElementById('feature-studio').scrollIntoView({behavior:'smooth'});">
<div class="h-16 w-16 rounded-full bg-[#2563eb] flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/20">
<span class="material-symbols-outlined text-white text-3xl">directions_walk</span>
</div>
<div class="flex-1 text-left">
<h3 class="text-2xl font-bold text-on-surface mb-1">Interactive Walkthroughs</h3>
<p class="text-on-surface-variant text-body-md">Guided pathfinding through complex indoor environments using LiDAR and SLAM.</p>
</div>
<div class="h-12 w-12 rounded-full bg-surface-container flex items-center justify-center text-slate-400 group-hover:bg-primary group-hover:text-on-primary transition-colors">
<span class="material-symbols-outlined">arrow_forward</span>
</div>
</div>
<!-- Camera Guidance -->
<div class="bg-primary-container/10 rounded-[2rem] p-8 flex items-center gap-6 shadow-xl hover:shadow-2xl transition-all cursor-pointer group" onclick="nav('scene');">
<div class="h-16 w-16 rounded-full bg-[#2563eb] flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/20">
<span class="material-symbols-outlined text-white text-3xl">videocam</span>
</div>
<div class="flex-1 text-left">
<h3 class="text-2xl font-bold text-on-surface mb-1">Camera Guidance</h3>
<p class="text-on-surface-variant text-body-md">Real-time sensory augmentation and object labeling for immediate awareness.</p>
</div>
<div class="h-12 w-12 rounded-full bg-surface-container flex items-center justify-center text-slate-400 group-hover:bg-primary group-hover:text-on-primary transition-colors">
<span class="material-symbols-outlined">arrow_forward</span>
</div>
</div>
<!-- Upload Troubleshooting -->
<div class="bg-primary-container/10 rounded-[2rem] p-8 flex items-center gap-6 shadow-xl hover:shadow-2xl transition-all cursor-pointer group" onclick="nav('ocr');">
<div class="h-16 w-16 rounded-full bg-[#2563eb] flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/20">
<span class="material-symbols-outlined text-white text-3xl">upload_file</span>
</div>
<div class="flex-1 text-left">
<h3 class="text-2xl font-bold text-on-surface mb-1">Upload Troubleshooting</h3>
<p class="text-on-surface-variant text-body-md">Analyze documents, forms, and technical manuals with layout-aware OCR.</p>
</div>
<div class="h-12 w-12 rounded-full bg-surface-container flex items-center justify-center text-slate-400 group-hover:bg-primary group-hover:text-on-primary transition-colors">
<span class="material-symbols-outlined">arrow_forward</span>
</div>
</div>
<!-- AI Feature Studio -->
<div class="bg-primary-container/10 rounded-[2rem] p-8 flex items-center gap-6 shadow-xl hover:shadow-2xl transition-all cursor-pointer group" onclick="document.getElementById('feature-studio').scrollIntoView({behavior:'smooth'});">
<div class="h-16 w-16 rounded-full bg-[#2563eb] flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/20">
<span class="material-symbols-outlined text-white text-3xl">auto_awesome</span>
</div>
<div class="flex-1 text-left">
<h3 class="text-2xl font-bold text-on-surface mb-1">AI Feature Studio</h3>
<p class="text-on-surface-variant text-body-md">Custom accessibility modules tailored to your specific environmental needs.</p>
</div>
<div class="h-12 w-12 rounded-full bg-surface-container flex items-center justify-center text-slate-400 group-hover:bg-primary group-hover:text-on-primary transition-colors">
<span class="material-symbols-outlined">arrow_forward</span>
</div>
</div>
<!-- New Sixth Card: Real-time Translation -->
<div class="bg-primary-container/10 rounded-[2rem] p-8 flex items-center gap-6 shadow-xl hover:shadow-2xl transition-all cursor-pointer group" onclick="nav('sign_language');">
<div class="h-16 w-16 rounded-full bg-[#2563eb] flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/20">
<span class="material-symbols-outlined text-white text-3xl">translate</span>
</div>
<div class="flex-1 text-left">
<h3 class="text-2xl font-bold text-on-surface mb-1">FAQ &amp; Accessibility</h3>
<p class="text-on-surface-variant text-body-md">Instant visual translation of text and signage into over 100 languages.</p>
</div>
<div class="h-12 w-12 rounded-full bg-surface-container flex items-center justify-center text-slate-400 group-hover:bg-primary group-hover:text-on-primary transition-colors">
<span class="material-symbols-outlined">arrow_forward</span>
</div>
</div></div><div class="mt-16 w-full max-w-4xl mx-auto">
<div class="flex items-center gap-3 mb-8">
<span class="material-symbols-outlined text-primary">bolt</span>
<h2 class="font-headline-md text-headline-md text-on-background">Instant Accessibility Actions &amp; Recommended Questions</h2>
</div>
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
<div class="glass-card p-4 rounded-xl border border-outline-variant/20 flex items-center gap-3 hover:bg-primary-container/10 transition-all cursor-pointer" onclick="nav('ocr');">
<span class="text-xl">🤘</span>
<span class="text-body-sm text-on-surface">'I want to understand this sign'</span>
</div>
<div class="glass-card p-4 rounded-xl border border-outline-variant/20 flex items-center gap-3 hover:bg-primary-container/10 transition-all cursor-pointer" onclick="nav('emotion');">
<span class="text-xl">😊</span>
<span class="text-body-sm text-on-surface">'I want to know how this person feels'</span>
</div>
<div class="glass-card p-4 rounded-xl border border-outline-variant/20 flex items-center gap-3 hover:bg-primary-container/10 transition-all cursor-pointer" onclick="document.getElementById('chat-studio').scrollIntoView({behavior:'smooth'});">
<span class="material-symbols-outlined text-outline text-lg">build</span>
<span class="text-body-sm text-on-surface">'Why is my prediction incorrect?'</span>
</div>
<div class="glass-card p-4 rounded-xl border border-outline-variant/20 flex items-center gap-3 hover:bg-primary-container/10 transition-all cursor-pointer" onclick="nav('ocr');">
<span class="text-xl">📖</span>
<span class="text-body-sm text-on-surface">'I have a picture with Bengali text'</span>
</div>
<div class="glass-card p-4 rounded-xl border border-outline-variant/20 flex items-center gap-3 hover:bg-primary-container/10 transition-all cursor-pointer" onclick="nav('scene');">
<span class="text-xl">🌍</span>
<span class="text-body-sm text-on-surface">'I am blind, please describe this image'</span>
</div>
<div class="glass-card p-4 rounded-xl border border-outline-variant/20 flex items-center gap-3 hover:bg-primary-container/10 transition-all cursor-pointer" onclick="document.getElementById('chat-studio').scrollIntoView({behavior:'smooth'});">
<span class="text-xl">🧠</span>
<span class="text-body-sm text-on-surface">'How do the AI models work?'</span>
</div>
</div>
</div>
<!-- Dashboard Mockup/Image -->
</div>
</section>
<!-- Interactive Actions Grid -->
<section class="py-24 px-8 bg-surface-container-lowest">
<div class="max-w-7xl mx-auto">
<div class="mb-16">
<h2 class="font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-background mb-4">Instant Accessibility Actions</h2>
<p class="text-body-md text-on-surface-variant max-w-xl">Harness Nova's vision models to interpret your environment in milliseconds.</p>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
<!-- Action Cards -->
<div class="glass-card p-8 rounded-2xl flex flex-col gap-6 group cursor-pointer" onclick="nav('ocr');" title="Open OCR &amp; TTS Mode">
<div class="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary transition-colors">
<span class="material-symbols-outlined text-primary group-hover:text-on-primary" style="font-variation-settings: 'FILL' 1;">signpost</span>
</div>
<div>
<h3 class="font-headline-md text-headline-md mb-2">Understand signs</h3>
<p class="text-body-sm text-on-surface-variant">OCR and context-aware interpretation of complex public signage.</p>
</div>
<div class="mt-auto flex items-center gap-2 text-primary font-label-md text-label-md">
                        Try Action <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
</div>
</div>
<div class="glass-card p-8 rounded-2xl flex flex-col gap-6 group cursor-pointer" onclick="nav('emotion');" title="Open Emotion Detection Mode">
<div class="h-12 w-12 rounded-xl bg-tertiary/10 flex items-center justify-center group-hover:bg-tertiary transition-colors">
<span class="material-symbols-outlined text-tertiary group-hover:text-on-tertiary" style="font-variation-settings: 'FILL' 1;">sentiment_satisfied</span>
</div>
<div>
<h3 class="font-headline-md text-headline-md mb-2">Social Emotion</h3>
<p class="text-body-sm text-on-surface-variant">Real-time emotional analysis and social cue descriptions.</p>
</div>
<div class="mt-auto flex items-center gap-2 text-tertiary font-label-md text-label-md">
                        Try Action <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
</div>
</div>
<div class="glass-card p-8 rounded-2xl flex flex-col gap-6 group cursor-pointer" onclick="nav('scene');" title="Open Scene Description Mode">
<div class="h-12 w-12 rounded-xl bg-secondary/10 flex items-center justify-center group-hover:bg-secondary transition-colors">
<span class="material-symbols-outlined text-secondary group-hover:text-on-secondary" style="font-variation-settings: 'FILL' 1;">restaurant</span>
</div>
<div>
<h3 class="font-headline-md text-headline-md mb-2">Identify Objects</h3>
<p class="text-body-sm text-on-surface-variant">Dense object labeling for navigating unfamiliar indoor spaces.</p>
</div>
<div class="mt-auto flex items-center gap-2 text-secondary font-label-md text-label-md">
                        Try Action <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
</div>
</div>
<div class="glass-card p-8 rounded-2xl flex flex-col gap-6 group cursor-pointer" onclick="nav('ocr');" title="Open Document Scan Mode">
<div class="h-12 w-12 rounded-xl bg-primary-fixed-dim/10 flex items-center justify-center group-hover:bg-primary-fixed-dim transition-colors">
<span class="material-symbols-outlined text-primary-fixed-dim group-hover:text-on-primary-fixed" style="font-variation-settings: 'FILL' 1;">description</span>
</div>
<div>
<h3 class="font-headline-md text-headline-md mb-2">Document Scan</h3>
<p class="text-body-sm text-on-surface-variant">Layout-aware reading of forms, mail, and technical manuals.</p>
</div>
<div class="mt-auto flex items-center gap-2 text-primary-fixed-dim font-label-md text-label-md">
                        Try Action <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
</div>
</div>
</div>
</div>
</section>
<!-- Chat Studio Interface -->
<section id="chat-studio" class="py-24 px-8 relative overflow-hidden">
<div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
<div class="order-2 lg:order-1">
<div class="relative w-full aspect-[4/3] rounded-3xl bg-surface-container border border-glass-border shadow-2xl overflow-hidden flex flex-col">
<!-- Chat Header -->
<div class="px-6 py-4 border-b border-outline-variant/30 flex justify-between items-center bg-surface-container-high/50">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-nova-gradient-start flex items-center justify-center">
<span class="material-symbols-outlined text-[18px] text-on-primary" style="font-variation-settings: 'FILL' 1;">bolt</span>
</div>
<span class="font-headline-md text-[16px]">Nova AI Chat</span>
</div>
<span class="text-code-md font-code-md text-outline">Session: 829-X</span>
</div>
<!-- Chat Body -->
<div class="flex-1 p-6 flex flex-col gap-6 overflow-y-auto scroll-mask">
<div class="flex justify-end">
<div class="bg-primary-container/10 border border-primary-container/20 p-4 rounded-2xl rounded-tr-none max-w-[80%]">
<p class="text-body-md text-primary">"What does the street sign in front of me say?"</p>
</div>
</div>
<div class="flex gap-3">
<div class="w-8 h-8 shrink-0 rounded-full bg-nova-gradient-end flex items-center justify-center">
<span class="material-symbols-outlined text-[18px] text-on-tertiary" style="font-variation-settings: 'FILL' 1;">auto_awesome</span>
</div>
<div class="bg-surface-container-high p-4 rounded-2xl rounded-tl-none border border-outline-variant/20 max-w-[85%]">
<p class="text-body-md mb-2">Analyzing scene... I've detected a "Caution: Steep Grade" sign with a yellow background. Below it, there's a smaller text that says "Engage Low Gear."</p>
<div class="p-3 bg-background/50 rounded-lg border border-outline-variant/10 flex items-center gap-3 mt-3">
<span class="material-symbols-outlined text-tertiary">warning</span>
<span class="text-body-sm text-on-surface-variant italic">Note: The path ahead has a 12% incline.</span>
</div>
</div>
</div>
</div>
<!-- Input Mockup -->
<div class="p-6 bg-surface-container-high/50 border-t border-outline-variant/30">
<div class="w-full bg-surface-container-low border border-outline-variant/50 rounded-xl px-4 py-3 flex justify-between items-center">
<span class="text-on-surface-variant text-body-sm">Ask Nova anything...</span>
<div class="flex gap-2">
<span class="material-symbols-outlined text-outline">mic</span>
<span class="material-symbols-outlined text-primary">send</span>
</div>
</div>
</div>
<!-- Background Atmospheric Shader -->
</div>
</div>
<div class="order-1 lg:order-2">
<h2 class="font-headline-lg text-headline-lg-mobile md:text-headline-lg mb-6">Neural Chat Studio</h2>
<p class="text-body-lg text-on-surface-variant mb-8">
                    Experience conversations that feel human but process with machine precision. Nova doesn't just read text; it understands depth, lighting, and semantic intent.
                </p>
<ul class="space-y-4">
<li class="flex items-start gap-4">
<span class="material-symbols-outlined text-nova-gradient-start mt-1">check_circle</span>
<div>
<span class="block font-headline-md text-[18px]">Multi-Modal Intelligence</span>
<p class="text-body-sm text-on-surface-variant">Combines vision, audio, and spatial telemetry into one chat thread.</p>
</div>
</li>
<li class="flex items-start gap-4">
<span class="material-symbols-outlined text-nova-gradient-start mt-1">check_circle</span>
<div>
<span class="block font-headline-md text-[18px]">Zero Latency Edge AI</span>
<p class="text-body-sm text-on-surface-variant">Processed locally for immediate life-critical responses.</p>
</div>
</li>
</ul>
<button class="mt-10 px-8 py-3 bg-nova-gradient-start text-on-primary rounded-xl font-label-md text-label-md hover:brightness-110 transition-all cta-press shadow-xl shadow-primary/20" onclick="nav('sign_language');">
                    Try the Demo
                </button>
</div>
</div>
</section>
<!-- Feature Studio Tabs -->
<section id="feature-studio" class="py-24 px-8 bg-surface-container-low">
<div class="max-w-7xl mx-auto">
<div class="text-center mb-16">
<h2 class="font-headline-lg text-headline-lg-mobile md:text-headline-lg mb-4">AI Feature Studio</h2>
<div class="flex flex-wrap justify-center gap-2 mt-8">
<button class="px-6 py-3 rounded-full bg-primary text-on-primary font-label-md text-label-md shadow-lg shadow-primary/30" onclick="nav('sign_language');">Interactive Walkthroughs</button>
<button class="px-6 py-3 rounded-full hover:bg-surface-variant text-on-surface-variant font-label-md text-label-md transition-colors" onclick="nav('scene');">Camera Guidance</button>
<button class="px-6 py-3 rounded-full hover:bg-surface-variant text-on-surface-variant font-label-md text-label-md transition-colors" onclick="nav('ocr');">Feature Studio</button>
</div>
</div>
<div class="glass-card rounded-[2rem] p-1 gap-1 flex flex-col md:flex-row overflow-hidden min-h-[400px]">
<div class="w-full md:w-1/2 p-12 flex flex-col justify-center">
<h3 class="font-headline-lg mb-6">Guided Pathfinding</h3>
<p class="text-body-lg text-on-surface-variant mb-8 leading-relaxed">
                        Nova uses advanced LiDAR and SLAM technologies to create a virtual rail system. It guides you through complex indoor environments like airports and malls with haptic and audio feedback.
                    </p>
<div class="flex gap-4">
<div class="bg-surface-variant/50 p-4 rounded-xl border border-outline-variant/30 flex-1">
<span class="block font-code-md text-primary text-[20px] mb-1">99.9%</span>
<span class="block text-label-md text-outline uppercase tracking-tighter">Precision</span>
</div>
<div class="bg-surface-variant/50 p-4 rounded-xl border border-outline-variant/30 flex-1">
<span class="block font-code-md text-tertiary text-[20px] mb-1">15ms</span>
<span class="block text-label-md text-outline uppercase tracking-tighter">Latency</span>
</div>
</div>
</div>
<div class="w-full md:w-1/2 min-h-[300px] relative">
<div class="absolute inset-0 bg-cover bg-center" data-alt="A futuristic 3D visualization of an indoor navigation map. Glowing blue path lines are superimposed over a dark, wireframe structure of a large terminal. The style is technical and sleek with neon cyan accents, mirroring the SensAI brand identity. Low lighting with high-contrast UI elements." style="background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuBiF7CyMjOeqaI8mzJ7LhjDqJXeO8KllI5ph2NtUHZeLCSotZf-Cz0001ewXjUM-FzVpkZ52s0Ag4a2uRCTIUsrFWwfWIyD_Hk2JGIqSoI3aiVO7R_RwD8k01lDjU1arjoTUbq-dJtGctzyQ-7Su5PELLOxvx3MicUt7pOMxSrEZl2zPF8obWm95bscPMON4XsppG00zL7_IoIPN13s5QmeX9-aYfevYRbSFt98YR-HfuhOA_CfHeHP'); background-color: #0d1320;"></div>
<div class="absolute inset-0 bg-gradient-to-r from-surface-container via-transparent to-transparent"></div>
</div>
</div>
</div>
</section>
<!-- Footer Anchor -->
<footer class="w-full py-12 border-t border-[#46465d]/15 bg-[#0c0c20]">
<div class="flex flex-col md:flex-row justify-between items-center max-w-7xl mx-auto px-8 gap-6">
<div class="flex items-center gap-3" onclick="nav('home')" style="cursor:pointer;" title="SensAI Home">
<img alt="Nova Logo" class="h-8 w-8" src="LOGO_DARK_PLACEHOLDER">
<span class="text-lg font-bold text-[#e5e3ff]">SensAI</span>
</div>
<p class="text-[#e5e3ff]/50 font-['Inter'] text-sm text-center">© 2024 SensAI. Built for the Luminous Observer.</p>
<div class="flex gap-6">
<a class="text-[#e5e3ff]/50 hover:text-[#00e3fd] transition-colors font-['Inter'] text-sm" onclick="openModal('about')" style="cursor:pointer;">Documentation</a>
<a class="text-[#e5e3ff]/50 hover:text-[#00e3fd] transition-colors font-['Inter'] text-sm" onclick="openModal('about')" style="cursor:pointer;">Privacy</a>
<a class="text-[#e5e3ff]/50 hover:text-[#00e3fd] transition-colors font-['Inter'] text-sm" onclick="openModal('about')" style="cursor:pointer;">Terms</a>
<a class="text-[#e5e3ff]/50 hover:text-[#00e3fd] transition-colors font-['Inter'] text-sm" onclick="openModal('contact')" style="cursor:pointer;">Support</a>
</div>
</div>
</footer>
<!-- Interactive Layer: Floating FAB for Mobile Context -->
<button class="fixed bottom-8 right-8 md:hidden h-14 w-14 rounded-full bg-primary-container text-on-primary-container shadow-2xl flex items-center justify-center pulse-live z-50">
<span class="material-symbols-outlined">visibility</span>
</button>
<script>
        // Micro-interaction for cards
        document.querySelectorAll('.glass-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                // Potential hover sound or subtle haptic simulation
            });
        });

        // Simple Smooth Scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        });

        var ddOpen = false;
        function toggleDD() {
            var dd = document.getElementById('aiDD');
            if (!dd) return;
            ddOpen = !ddOpen;
            if (ddOpen) {
                dd.classList.add('open');
            } else {
                dd.classList.remove('open');
            }
        }

        document.addEventListener('click', function(e) {
            var dd = document.getElementById('aiDD');
            if (dd && !dd.contains(e.target)) {
                dd.classList.remove('open');
                ddOpen = false;
            }
        });

        function nav(mode){
          try {
            var win = window.parent || window.top || window;
            var url = new URL(win.location.href);
            url.hash = '';
            url.searchParams.set('mode', mode);
            win.location.href = url.toString();
          } catch(e) {
            try {
              var topUrl = new URL(window.top.location.href);
              topUrl.hash = '';
              topUrl.searchParams.set('mode', mode);
              window.top.location.href = topUrl.toString();
            } catch(err) {
              window.location.href = '/?mode=' + encodeURIComponent(mode);
            }
          }
        }

        function openModal(m){
          try {
            var win = window.parent || window.top || window;
            var url = new URL(win.location.href);
            url.hash = '';
            url.searchParams.set('modal', m);
            win.location.href = url.toString();
          } catch(e) {
            try {
              var topUrl = new URL(window.top.location.href);
              topUrl.hash = '';
              topUrl.searchParams.set('modal', m);
              window.top.location.href = topUrl.toString();
            } catch(err) {
              window.location.href = '/?modal=' + encodeURIComponent(m);
            }
          }
        }
    </script>
</body></html>"""
    return raw_html.replace("LOGO_DARK_PLACEHOLDER", LOGO_DARK_B64)


def render_nova_page(tts=None) -> None:
    """
    Renders Nova AI Accessibility Assistant page with full interactive Streamlit backend logic.
    """
    from modes.nova_assistant import NovaAssistantMode
    mode_obj = NovaAssistantMode(tts=tts)
    mode_obj.render()

