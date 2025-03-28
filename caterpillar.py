import re
import logging
from os import path
from urllib.parse import urlparse
import requests



class Caterpillar:
    def __init__(self, *plugins_, **settings_):
        self.plugins = list(plugins_)
        self.settings = settings_
        logging.getLogger().handlers = []  # Clear any previous handlers

        if self.settings.get('silenced', False) == True:
            logging.basicConfig(
                level=logging.CRITICAL,  
                format='%(asctime)s - %(message)s',  
                handlers=[]  
            )
        else:
            logging.basicConfig(
                level=logging.INFO,  
                format='%(asctime)s - %(message)s',  
                handlers=[logging.StreamHandler()].extend(self.settings.get('handlers', []))
            )
    
        self.patterns = [    
        #   REGEX                                   COMMENT                 IGNORE INNER REGEX?   
            r'^@([1-6])\s(.*?)$',                   # headings                  
            r'^>\s(.*?)$',                          # blockquote                
            r'^#\s(.*?)$',                          # code (full line)      !   
            r'\*\*(.*?)\*\*',                       # bold                      
            r'//(.*?)//',                           # italic                    
            r'__(.*?)__',                           # underline                 
            r'--(.*?)--',                           # strikethrough             
            r'##(.*?)##',                           # highlighted               
            r'``(.*?)``',                           # code (inline)         !   
            r'\!\((.*?)\)\[(.*?)\]',                # link                  !   
            r'\!\[(.*?)\]\[(.*?)\]\[(.*?):(.*?)\]', # picture               !   
            r'^\+\s(.*?)$',                         # list (unordered)          
            r'\[\!\](.*?)\[\!\]'                    # leave as-is (block)   !   
        ]

        self.capture_patterns = [                                  
            r'^@[1-6]\s.*?$',                   
            r'^>\s.*?$',                          
            r'^#\s.*?$',                          
            r'\*\*.*?\*\*',                       
            r'//.*?//',                           
            r'__.*?__',                           
            r'--.*?--',                           
            r'##.*?##',                           
            r'``.*?``',                           
            r'\!\(.*?\)\[.*?\]',                
            r'\!\[.*?\]\[.*?\]\[.*?:.*?\]', 
            r'^\+\s.*?$',                         
            r'\[\!\].*?\[\!\]'                      
        ]
        # plugins removal
    def addPlugins(self, *plugins):
        for plugin in plugins:
            if not plugin in self.plugins:
                self.plugins.append(plugin)
                logging.info("plugin '" + str(plugin) + "' was added")
            else:
                logging.info("plugin '" + str(plugin) + "' failed to add")
        # plugins removal
    def removePlugins(self, *plugins):
        for plugin in plugins:
            if plugin in self.plugins:
                self.plugins.remove(plugin)
                logging.info("plugin '" + str(plugin) + "' was removed")
            else:
                logging.info("plugin '" + str(plugin) + "' failed to remove")
    
        # settings update
    def updateSettings(self, **settings_):
        self.settings = settings_
        # silenced
        if self.settings.get('silenced', False) == True:
            logging.basicConfig(
                level=logging.CRITICAL,  
                format='%(asctime)s - %(message)s',  
                handlers=[]  
            )
        else:
            logging.basicConfig(
                level=logging.INFO,  
                format='%(asctime)s - %(message)s',  
                handlers=[logging.StreamHandler()].extend(self.settings.get('handlers', []))
            )
    
        # PARSING       
    def parseText(self, text_ : str):

        text = text_
        ########################### plugin exec at pos (todo : make a func)
        # for plugin in exec_pos_0:                         
        #     try:
        #         if path.isfile(str(plugin[0])):
        #             plug = open(str(plugin[0]), "r", encoding=self.settings.get("encoding", "utf-8")).read()
        #         elif bool(urlparse(plugin).netloc) == True:
        #             plug = requests.get(str(plugin[0]), headers={'Cache-Control': 'no-cache','Pragma': 'no-cache'})
        #             if plug.status_code == 200:
        #                 plug = plug.text
        #         else:
        #             plug = (plugin[0])
        #         local_vars = {}
        #         exec(plug, globals(), local_vars)
        #         plugin.pop(0)
        #         plugin.pop(0)
        #         if "main" in local_vars:
        #             text, self = local_vars["main"](text, self, plugin)
    
        #         logging.info("plugin '" + str(plugin[0]) + "' executed")
        #     except:
        #         logging.info("plugin '" + str(plugin[0]) + "' failed to execute")

        exec_pos_0 = []
        exec_pos_1 = []
        exec_pos_2 = []
        exec_pos_3 = []
        exec_pos_4 = []
        logging.info("started parsing")

        for plugin in self.plugins:
            if plugin[1] == 0:
                exec_pos_0.append(plugin)
            elif plugin[1] == 1:
                exec_pos_1.append(plugin)
            elif plugin[1] == 2:
                exec_pos_2.append(plugin)
            elif plugin[1] == 3:
                exec_pos_3.append(plugin)
            elif plugin[1] == 4:
                exec_pos_4.append(plugin)

    
        for plugin in exec_pos_0:                         
            try:
                if path.isfile(str(plugin[0])):
                    plug = open(str(plugin[0]), "r", encoding=self.settings.get("encoding", "utf-8")).read()
                elif bool(urlparse(plugin).netloc) == True:
                    plug = requests.get(str(plugin[0]), headers={'Cache-Control': 'no-cache','Pragma': 'no-cache'})
                    if plug.status_code == 200:
                        plug = plug.text
                else:
                    plug = (plugin[0])
                local_vars = {}
                exec(plug, globals(), local_vars)
                if "main" in local_vars:
                    text, self = local_vars["main"](text, self, plugin)
    
                logging.info("plugin '" + str(plugin[0]) + "' executed")
            except:
                logging.info("plugin '" + str(plugin[0]) + "' failed to execute")


        # WORKING WITH THOSE WITH "!" ("I" column) - left as-is no other regex parsing
        as_is_elements = []
        as_is_elements.extend(re.findall(self.patterns[2], text, re.MULTILINE))
        text = re.sub(self.capture_patterns[2], "# text", text, 0, re.MULTILINE)
        as_is_elements.extend(re.findall(self.patterns[8], text, re.DOTALL))
        text = re.sub(self.capture_patterns[8], "``text``", text, 0, re.DOTALL)
        as_is_elements.extend(re.findall(self.patterns[9], text))
        text = re.sub(self.capture_patterns[9], "!(text)[text]", text, 0)
        as_is_elements.extend(re.findall(self.patterns[10], text))
        text = re.sub(self.capture_patterns[10], "![text][text][text:text]", text, 0)
        as_is_elements.extend(re.findall(self.patterns[12], text, re.DOTALL))
        text = re.sub(self.capture_patterns[12], "[!]text[!]", text, 0, re.DOTALL)

        logging.info("removed as-is elements")

        for plugin in exec_pos_1:                         
            try:
                if path.isfile(str(plugin[0])):
                    plug = open(str(plugin[0]), "r", encoding=self.settings.get("encoding", "utf-8")).read()
                elif bool(urlparse(plugin).netloc) == True:
                    plug = requests.get(str(plugin[0]), headers={'Cache-Control': 'no-cache','Pragma': 'no-cache'})
                    if plug.status_code == 200:
                        plug = plug.text
                else:
                    plug = (plugin[0])
                local_vars = {}
                exec(plug, globals(), local_vars)
                if "main" in local_vars:
                    text, self = local_vars["main"](text, self, plugin)
    
                logging.info("plugin '" + str(plugin[0]) + "' executed")
            except:
                logging.info("plugin '" + str(plugin[0]) + "' failed to execute")

        # TEXT MODIFIERS
        text = re.sub(self.patterns[3], r'<b>\1</b>', text, 0, re.DOTALL)
        text = re.sub(self.patterns[4], r'<i>\1</i>', text, 0, re.DOTALL)
        text = re.sub(self.patterns[5], r'<u>\1</u>', text, 0, re.DOTALL)
        text = re.sub(self.patterns[6], r'<s>\1</s>', text, 0, re.DOTALL)
        text = re.sub(self.patterns[7], r'<mark>\1</mark>', text, 0, re.DOTALL)
        
        logging.info("parsed text modifiers")

        for plugin in exec_pos_2:                         
            try:
                if path.isfile(str(plugin[0])):
                    plug = open(str(plugin[0]), "r", encoding=self.settings.get("encoding", "utf-8")).read()
                elif bool(urlparse(plugin).netloc) == True:
                    plug = requests.get(str(plugin[0]), headers={'Cache-Control': 'no-cache','Pragma': 'no-cache'})
                    if plug.status_code == 200:
                        plug = plug.text
                else:
                    plug = (plugin[0])
                local_vars = {}
                exec(plug, globals(), local_vars)
                if "main" in local_vars:
                    text, self = local_vars["main"](text, self, plugin)
    
                logging.info("plugin '" + str(plugin[0]) + "' executed")
            except:
                logging.info("plugin '" + str(plugin[0]) + "' failed to execute")

        # HEADINGS
        text = re.sub(self.patterns[0], r'<h\1>\2</h\1>', text, 0, re.MULTILINE)
        logging.info("parsed headings")

        # BLOCKQUOTE
        text = re.sub(self.patterns[1], r'<blockquote>\1</blockquote>', text, 0, re.MULTILINE)
        logging.info("parsed blockquotes")

        # UNORDERED LIST
        text = re.sub(self.patterns[11], r'<li>\1</li>', text, 0, re.MULTILINE)
        logging.info("parsed lists")

        for plugin in exec_pos_3:                         
            try:
                if path.isfile(str(plugin[0])):
                    plug = open(str(plugin[0]), "r", encoding=self.settings.get("encoding", "utf-8")).read()
                elif bool(urlparse(plugin).netloc) == True:
                    plug = requests.get(str(plugin[0]), headers={'Cache-Control': 'no-cache','Pragma': 'no-cache'})
                    if plug.status_code == 200:
                        plug = plug.text
                else:
                    plug = (plugin[0])
                local_vars = {}
                exec(plug, globals(), local_vars)
                if "main" in local_vars:
                    text, self = local_vars["main"](text, self, plugin)
    
                logging.info("plugin '" + str(plugin[0]) + "' executed")
            except:
                logging.info("plugin '" + str(plugin[0]) + "' failed to execute")

        # REINSERTING AS-IS ELEMENTS
        idx = 0
        found_elements = re.findall(self.capture_patterns[2], text, re.MULTILINE)
        for i in range(len(found_elements)):
            text = text.replace(found_elements[i], "<code>"+as_is_elements[idx]+"</code>", 1)
            idx += 1
        found_elements = re.findall(self.capture_patterns[8], text, re.DOTALL)
        for i in range(len(found_elements)):
            text = text.replace(found_elements[i], "<code>"+as_is_elements[idx]+"</code>", 1)
            idx += 1
        found_elements = re.findall(self.capture_patterns[9], text, re.DOTALL)
        for i in range(len(found_elements)):
            text = text.replace(found_elements[i], "<a href="+as_is_elements[idx][0]+">"+as_is_elements[idx][1]+"</a>", 1)
            idx += 1
        found_elements = re.findall(self.capture_patterns[10], text, re.DOTALL)
        for i in range(len(found_elements)):
            text = text.replace(found_elements[i], f"<img src='{as_is_elements[idx][0]}' alt='{as_is_elements[idx][1]}' width='{as_is_elements[idx][2]}' height='{as_is_elements[idx][3]}'>", 1)
            idx += 1
        found_elements = re.findall(self.capture_patterns[12], text, re.DOTALL)
        for i in range(len(found_elements)):
            text = text.replace(found_elements[i], as_is_elements[idx], 1)
            idx += 1
        logging.info("inserted as-is elements")

        # PARSING NEWLINES

        text = text.replace("\n", "<br>\n")
        text = text.replace("<br>\n<br>\n", "<br>\n")
        logging.info("parsed newlines")

        for plugin in exec_pos_4:                         
            try:
                if path.isfile(str(plugin[0])):
                    plug = open(str(plugin[0]), "r", encoding=self.settings.get("encoding", "utf-8")).read()
                elif bool(urlparse(plugin).netloc) == True:
                    plug = requests.get(str(plugin[0]), headers={'Cache-Control': 'no-cache','Pragma': 'no-cache'})
                    if plug.status_code == 200:
                        plug = plug.text
                else:
                    plug = (plugin[0])
                local_vars = {}
                exec(plug, globals(), local_vars)
                if "main" in local_vars:
                    text, self = local_vars["main"](text, self, plugin[2:])
    
                logging.info("plugin '" + str(plugin[0]) + "' executed")
            except:
                logging.info("plugin '" + str(plugin[0]) + "' failed to execute")
        
        
        
        logging.info("finished parsing")
        return text
        
        

    
