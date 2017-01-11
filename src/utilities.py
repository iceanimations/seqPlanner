'''
Created on Oct 29, 2015

@author: qurban.ali
'''
import sys
sys.path.append("R:/Pipe_Repo/Projects/TACTIC")
from auth import user

server = None

def setServer():
    errors = {}
    global server
    try:
        user.login('tactic', 'tactic123')
        server = user.get_server()
        server.set_project('test_mansour_ep')
    except Exception as ex:
        errors['Could not connect to TACTIC'] = str(ex)
    return errors
        
def getProjects():
    errors = {}
    projects = []
    if server:
        try:
            projects = server.eval("@GET(sthpw/project.code)")
        except Exception as ex:
            errors['Could not get the list of projects'] = str(ex)
    else:
        errors['Could not find the TACTIC server'] = ''
    return projects, errors
    
        
def setProject(project):
    errors = {}
    if server:
        try:
            server.set_project(project)
        except Exception as ex:
            errors['Could not set the project'] = str(ex)
    else:
        errors['Could not find the TACTIC server'] = ''
    return errors
        
def getEpisodes():
    eps = []
    errors = {}
    if server:
        try:
            eps = server.eval("@GET(vfx/episode.code)")
        except Exception as ex:
            errors['Could not get the list of episodes from TACTIC'] = str(ex)
    else:
        errors['Could not find the TACTIC server'] = ""
    return eps, errors

def existingSeqs(ep):
    errors = {}
    seqs = []
    try:
        seqs = server.eval("@GET(vfx/sequence['episode_code', '%s'].code)"%ep)
    except Exception as ex:
        errors['Could not find the existing Sequences'] = str(ex)
    return seqs, errors

def addSequences(ep, seqs):
    errors = {}
    existingSeq, err = existingSeqs(ep)
    if err: errors.update(err)
    if existingSeq:
        seqs = [seq for seq in seqs if '_'.join([ep, seq]).upper() not in existingSeq]
    if server:
        data = [{'episode_code': ep, 'code': '_'.join([ep, seq]).upper()} for seq in seqs]
        try:
            server.insert_multiple('vfx/sequence', data)
        except Exception as ex:
            errors['Could not insert the sequences'] = str(ex)
    else:
        errors['Could not find the server'] = ''
    return errors

def existingShots(ep):
    errors = {}
    shots = []
    try:
        shots = server.eval("@GET(vfx/sequence['episode_code', '%s'].vfx/shot.code)"%ep)
    except Exception as ex:
        errors['Could not find the existing shots'] = str(ex)
    return shots, errors
        
def addShots(ep, shots):
    errors = {}
    existingShot, err = existingShots(ep)
    if err: errors.update(err)
    if existingShot:
        tempShots = [shot for shot in shots if '_'.join([ep, shot]).upper() not in existingShot]
        for shot in shots.keys():
            if shot not in tempShots:
                shots.pop(shot, None)
    if server:
        data = [{'sequence_code': '_'.join([ep, shot.split('_')[0]]).upper(), 'code': '_'.join([ep, shot]).upper(),
                 'frame_in': fr[0], 'frame_out': fr[1], 'tc_frame_start': fr[0], 'tc_frame_end': fr[1]} for shot, fr in shots.items()]
        try:
            server.insert_multiple('vfx/shot', data)
        except Exception as ex:
            errors['Could not insert the shots'] = str(ex)
    else:
        errors['Could not find the server'] = ''
    return errors