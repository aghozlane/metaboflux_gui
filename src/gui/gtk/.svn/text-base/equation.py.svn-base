#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk, gobject
import re

class Equation:

    def __init__(self, parent, equation, dir, name, sbml):

        self.parent = parent
        self.equation = equation
        self.name = name
        self.sbml=sbml

        self.builder = gtk.Builder()
        self.builder.add_from_file(dir+"equation.glade")
        self.equation = self.builder.get_object("equation")

        # Get object from glade file
        self.remove_button = self.builder.get_object("remove_button")
        self.valid_button = self.builder.get_object("valid_button")
        self.equation_field = self.builder.get_object("equation_field")
        self.label_eq = self.builder.get_object("label_eq")
        self.radio = self.builder.get_object("radio")

        # Init widget
        self.parent.eq_box.pack_start(self.equation,
                               expand = False,
                               fill = False)
        self.remove_button.connect("clicked",
                            self.parent.remove_equation_widget,
                            self)
        self.valid_button.connect("clicked", self.valid_and_add_equation)

        self.welcome = "Enter your equation here."

    def set_equation(self, eq):
        if not eq:
            eq = self.welcome
        self.equation_field.set_text(eq)
        
    def valid_and_add_equation(self, widget):
        eq = self.equation_field.get_text()
        # Equation validation
        factors=eq.split()
        operators = ["+", "-", "*", "/", "=", ">", "<",">=","<="]
        list_all = []
        message = ""

        for r in self.sbml.reactions:
            list_all.append(self.sbml.get_name(r))
        for s in self.sbml.species:
            list_all.append(self.sbml.get_name(s))
            
        valid = True
 
        if not factors:
            message += "   * Equation is empty\n"
            valid = False
        else :
            isEquation = False
            # check if it is an equation
            for elem in factors:
                if (elem == "="or elem==">" or elem=="<"  or elem==">=" or elem=="<="):
                    isEquation = True
            
                #check if all factors exist
                if not elem in operators and not elem in list_all \
                       and not re.match("^[0-9]+[\.]?[0-9]*$", elem ) :
                    valid = False
                    message += "   *  \"" + elem+"\" did not exist.\n"
                    
                else :
                    pass
            
                # first and last member of the equation are not operators
            if (factors[0] in operators) or (factors[len(factors)-1] in operators) :
                valid = False
                message += "   * You can't begin or end your equation with an operator.\n"
         
            isOperator = False
            isFactor = False
        
            # find if there is more than one operator (or factor) after the other  
            for elem in factors:
                if ((elem in operators) and (isOperator)):
                    valid = False
                    message += "   * You have two (or more) neighbor operators\n"
                elif ((not elem in operators) and (isFactor)) :
                    valid = False
                    message +="   * An operator is missing\n"
                elif (not elem in operators) and (not isFactor) :
                    isOperator = False
                    isFactor = True
                elif (elem in operators) and (not isOperator) :
                    isOperator = True
                    isFactor = False
                else:
                    pass
    
            if not isEquation :
                valid = False
                message += "   * You have to put an equal to make an equation.\n"
        
        # After validation or not
        if valid:
            (set_kinetic, self.name) = self.parent.set_kinetic_law(factors, math = self.name)
        elif not valid and self.name and self.name in self.parent.get_kinetic_law().keys():
            self.parent.set_kinetic_law(math = self.name, delete = True)

        if valid and set_kinetic:
            self.disp_message("Your equation is valid.")
        else:
            self.disp_message("Not valid : \n" + message)

    def remove_equation(self):
        self.equation.destroy()
        if self.name:
            self.parent.set_kinetic_law(math = self.name, delete = True)

    def disp_message(self, message):
        self.label_eq.set_text(message)

    def add_sth(self, op):
        """
        Add sth to equation label
        """
        eq = self.equation_field.get_text()
        if eq == self.welcome:
            eq = ""
        if not op == "remove":
            eq += " " + op
        else:
            eq = " ".join(eq.split(" ")[:-1])

        self.equation_field.set_text(eq)
            
        
