#!/bin/bash
gunicorn attendo_frontend_calificador.wsgi:application --bind=0.0.0.0:8000
