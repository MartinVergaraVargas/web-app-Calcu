from flask import Blueprint, render_template, redirect, url_for

calculadora_bp = Blueprint('calculadora', __name__)

@calculadora_bp.route('/')
def index():
    return 'Esta es la calculaora'

@calculadora_bp.route('/add/<int:num1>/<int:num2>')
def add(num1, num2):
    return str(num1+num2)

@calculadora_bp.route('/sub/<int:num1>/<int:num2>')
def sub(num1, num2):
    return str(num1-num2)

@calculadora_bp.route('/multiply/<int:num1>/<int:num2>')
def multiply(num1, num2):
    return str(num1*num2)

@calculadora_bp.route('/ir-a-main')
def ir_a_main():
    return redirect(url_for('main.nosotros'))