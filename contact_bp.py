#global packages
from  flask import Flask, redirect, url_for, g, session, Blueprint, render_template
from jinja2 import Template
from flask import request
import time
import re
import copy

#local packages
from .contacts_data_classes import *
from  .validate import *
from . import global_var


contact_bp = Blueprint('contact', __name__, url_prefix='/contact')


def clean_search_str(keywords):
   keywords = (
     keywords.replace("+","\+")
            .replace("*", "\*")
            .replace("{", "\{")
            .replace("}", "\}")
            .replace("[", "\[")
            .replace("]", "\]")
            .replace("?", "\?")
            .replace("$", "\$")
            .replace("'\'", "\\")
             )
   return keywords


def html_error(error):
   return render_template('error.html', error = error)


def get_period(message=""):
   return render_template(
            'contact/get_period.html',
            err_message = message)
   

@contact_bp.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    form_dict = copy.deepcopy(form_dict_temp)
    if request.method == 'POST':
        form_dict = validate_contact_data(request, form_dict)
        valid_list = [
           element['valid'] for element in form_dict.values()]
        if False not in valid_list:
            res = global_var.contact_book.insert_contact(
                  ContactDict(form_dict))
            if res == 0:
                return render_template('contact/add_contact_OK.html')
            else:
               return html_error(res)
        else:
            return render_template(
                'contact/add_contact.html',
                form_dict=form_dict)
    else:
        return render_template(
             'contact/add_contact.html',
             form_dict=form_dict)
  

    
@contact_bp.route('/edit_contact', methods=['GET', 'POST'])
def edit_contact():
   results = []
   if request.method == 'POST':
       keywords = clean_search_str(request.form.get('Keywords'))
       for k in [kw for kw in keywords.strip().split(" ")]:
          result = global_var.contact_book.get_contacts(k)
          results.extend(result)
          return render_template(
                       'contact/contact_found.html',
                       result = results)   
   else:
      return render_template('contact/find_contact.html')           
        

@contact_bp.route('/edit_contact/<id>', methods=['GET', 'POST'])
def edit_contact_(id):
   form_dict = copy.deepcopy(form_dict_temp)
   if request.method == 'POST':
      form_dict = validate_contact_data(request, form_dict)
      valid_list = [val['valid'] for val in form_dict.values()]
      if False not in  valid_list:
         res= global_var.contact_book.update_contact(
                     id, ContactDict(form_dict))
         if res == 0:
            return render_template(
                     'contact/edit_contact_OK.html')
         else:
               return html_error(res)
      else:
            return render_template(
                     'contact/edit_contact.html',
                     form_dict=form_dict)

   else:
      contact = global_var.contact_book.get_contact_details(id)
      form_dict["Name"]["value"]= contact.name
      form_dict["Birthday"]["value"] = datetime.strptime(contact.birthday, "%d.%m.%Y").date().strftime("%Y-%m-%d")
      form_dict["Email"]["value"] = contact.email
      form_dict["Phone"]["value"] =  ", ".join(
                        [ph for ph in contact.phone])   
      form_dict["ZIP"]["value"] = contact.zip
      form_dict["Country"]["value"] = contact.country
      form_dict["Region"]["value"] = contact.region
      form_dict["City"]["value"] = contact.city
      form_dict["Street"]["value"] = contact.street
      form_dict["House"]["value"] = contact.house
      form_dict["Apartment"]["value"] = contact.apartment
      return render_template(
               'contact/edit_contact.html',
               form_dict=form_dict)

@contact_bp.route('/find_contact', methods=['GET', 'POST'])
def find_contact():
   results = []
   if request.method == 'POST':
      keywords = clean_search_str(request.form.get('Keywords'))
      for k in [kw for kw in keywords.strip().split(" ")]:
         for res in global_var.contact_book.get_contacts(k):
            if res not in results:
               results.append(res)
      return render_template(
                  'contact/contact_found.html',
                  result = results)    
   else:
      return render_template(
         'contact/find_contact.html')


@contact_bp.route('/show_all_contacts', methods=['GET', 'POST'])
def show_all_contacts():
   if request.method == 'POST':
      return redirect('/bot-command')
   else:
      result = global_var.contact_book.get_all_contacts()
      return render_template(
               'contact/all_contacts.html',
               result = result) 
        

@contact_bp.route('/contact_detail/<id>', methods=['GET', 'POST'])
def contact_detail(id):
   contact = global_var.contact_book.get_contact_details(id)
   return render_template('contact/contact_details.html',
                            contact = contact,
                            phone = contact.phone,
                            email = contact.email,
                            address = contact,
                            url='/find_contact')  

@contact_bp.route('/next_birthday', methods=['GET', 'POST'])
def next_birthday():
   message =""
   if request.method == 'POST':
      try:
         period = int(request.form.get('Period'))
         assert period > 0 and period < 365
      except:
         return get_period(
            "You could use numbers only, the period should be > 0 and < 365")  
      res = global_var.contact_book.get_birthday(period)
      return render_template(
                  'contact/birthday_contact_found.html',
                  days = request.form.get('Period'),
                  result = res)
   else:
      return get_period()

@contact_bp.route('/delete_contact', methods=['GET', 'POST'])
def delete_contact():
   results = []
   if request.method == 'POST':
      keywords = clean_search_str(request.form.get('Keywords'))
      for k in [kw for kw in keywords.strip().split(" ")]:
         results.extend(global_var.contact_book.get_contacts(k))
         return render_template(
                  'contact/contact_to_delete.html',
                  result = results) 
   else:
      return render_template('contact/search_contact_to_delete.html')

      
@contact_bp.route('/delete_contact/<id>', methods=['GET', 'POST'])
def contact_delete_(id):
   res = global_var.contact_book.delete_contact(id)
   if res ==0: 
      return render_template('contact/contact_delete_OK.html', id=id)
   else:
      return html_error(res)    
