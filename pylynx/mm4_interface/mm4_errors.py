# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 10:57:10 2023

@author: stefa
"""

class MM4Exception(Exception):
    pass

class NoWorkspace(MM4Exception):
    pass

class ApplicationBlocked(MM4Exception):
    pass

class EstopEngaged(MM4Exception):
    pass

class PermissionLevelNotUser(MM4Exception):
    pass

class MethodPermissionNotUser(MM4Exception):
    pass

class DevicesNotReady(MM4Exception):
    pass

class NotExecutionMode(MM4Exception):
    pass

class MethodAlreadyRunning(MM4Exception):
    pass

class UnknownVariable(MM4Exception):
    pass

class VariableIsReadOnly(MM4Exception):
    pass

class UnknownDevice(MM4Exception):
    pass

class UnknownWorktable(MM4Exception):
    pass

class UnknownQuery(MM4Exception):
    pass

class UnknownInput(MM4Exception):
    pass

class UnknownMethod(MM4Exception):
    pass

class PasswordNotValid(MM4Exception):
    pass

class NoMethodRunning(MM4Exception):
    pass

class CommandFormatNotRecognized(MM4Exception):
    pass

class ApplicationError(MM4Exception):
    pass

class ClientSideError(MM4Exception):
    pass

class SubMethodOnly(MM4Exception):
    pass

mm4_errors_dict = {
    1:"No Workspace",
    2:"Application Blocked",
    3:"Estop Engaged",
    4:"Permission Level Not User",
    5:"Method Permission Level Not User",
    6:"Devices Not Ready",
    7:"Not Execution Mode",
    8:"Method Already Running",
    9:"Unknown Variable",
    10:"Variable is Read Only",
    11:"Unknown Device",
    12:"Unknown Worktable",
    13:"Unknown Query",
    14:"Unknown Input",
    15:"Unknown Method",
    16:"Password Not Valid",
    17:"No Method Running",
    18:"A Command Format Was Not Recognized",
    19:"Application Error",
    20:"Client Side Error",
    21:"Sub Method Only"
    }