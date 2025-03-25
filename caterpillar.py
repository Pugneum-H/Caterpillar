import re
import importlib
import logging

def caterpillar(text_ : str, *plugins_, **settings_):

    plugins = plugins_
    settings = settings_
    text = text_

    logging.getLogger().handlers = []  # Clear any previous handlers

    if settings.get('silenced', False) == True:
        logging.basicConfig(
            level=logging.CRITICAL,  
            format='%(asctime)s - %(message)s',  
            handlers=[]  
        )
    else:
        logging.basicConfig(
            level=logging.INFO,  
            format='%(asctime)s - %(message)s',  
            handlers=[logging.StreamHandler()] 
        )
    



    text = text_

    logging.info("started parsing")



    patterns = [    
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
        r'\|\!\|(.*?)\|\!\|'                    # leave as-is (block)   !   
    ]

    capture_patterns = [                                  
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
        r'\|\!\|.*?\|\!\|'                      
    ]

    # PARSING 
     
    # WORKING WITH THOSE WITH "!" ("I" column) - left as-is no other regex parsing
    as_is_elements = []
    as_is_elements.extend(re.findall(patterns[2], text, re.MULTILINE))
    text = re.sub(capture_patterns[2], "# text", text, 0, re.MULTILINE)
    as_is_elements.extend(re.findall(patterns[8], text, re.DOTALL))
    text = re.sub(capture_patterns[8], "``text``", text, 0, re.DOTALL)
    as_is_elements.extend(re.findall(patterns[9], text))
    text = re.sub(capture_patterns[9], "!(text)[text]", text, 0)
    as_is_elements.extend(re.findall(patterns[10], text))
    text = re.sub(capture_patterns[10], "![text][text][text:text]", text, 0)
    as_is_elements.extend(re.findall(patterns[12], text, re.DOTALL))
    text = re.sub(capture_patterns[12], "|!|text|!|", text, 0, re.DOTALL)

    logging.info("removed as-is elements")

    # TEXT MODIFIERS
    text = re.sub(patterns[3], r'<b>\1</b>', text, 0, re.DOTALL)
    text = re.sub(patterns[4], r'<i>\1</i>', text, 0, re.DOTALL)
    text = re.sub(patterns[5], r'<u>\1</u>', text, 0, re.DOTALL)
    text = re.sub(patterns[6], r'<s>\1</s>', text, 0, re.DOTALL)
    text = re.sub(patterns[7], r'<mark>\1</mark>', text, 0, re.DOTALL)
    
    logging.info("parsed text modifiers")

    # HEADINGS
    text = re.sub(patterns[0], r'<h\1>\2</h\1>', text, 0, re.MULTILINE)
    logging.info("parsed headings")

    # BLOCKQUOTE
    text = re.sub(patterns[1], r'<blockquote>\1</blockquote>', text, 0, re.MULTILINE)
    logging.info("parsed blockquotes")

    # UNORDERED LIST
    text = re.sub(patterns[11], r'<li>\1</li>', text, 0, re.MULTILINE)
    logging.info("parsed lists")

    # REINSERTING AS-IS ELEMENTS
    idx = 0
    found_elements = re.findall(capture_patterns[2], text, re.MULTILINE)
    for i in range(len(found_elements)):
        text = text.replace(found_elements[i], "<code>"+as_is_elements[idx]+"</code>", 1)
        idx += 1
    found_elements = re.findall(capture_patterns[8], text, re.DOTALL)
    for i in range(len(found_elements)):
        text = text.replace(found_elements[i], "<code>"+as_is_elements[idx]+"</code>", 1)
        idx += 1
    found_elements = re.findall(capture_patterns[9], text, re.DOTALL)
    for i in range(len(found_elements)):
        text = text.replace(found_elements[i], "<a href="+as_is_elements[idx][0]+">"+as_is_elements[idx][1]+"</a>", 1)
        idx += 1
    found_elements = re.findall(capture_patterns[10], text, re.DOTALL)
    for i in range(len(found_elements)):
        text = text.replace(found_elements[i], f"<img src='{as_is_elements[idx][0]}' alt='{as_is_elements[idx][1]}' width='{as_is_elements[idx][2]}' height='{as_is_elements[idx][3]}'>", 1)
        idx += 1
    found_elements = re.findall(capture_patterns[12], text, re.DOTALL)
    for i in range(len(found_elements)):
        text = text.replace(found_elements[i], as_is_elements[idx], 1)
        idx += 1
    logging.info("inserted as-is elements")

    text = text.replace("\n", "<br>\n")
    text = text.replace("<br>\n<br>\n", "<br>\n")
    logging.info("parsing newlines")

    for plugin in plugins:
        try:
            plug = importlib.import_module(plugin)
            text, plugins, settings = plug.main(text, patterns, capture_patterns, plugins, settings)
            logging.info("plugin '" + str(plugin) + "' loaded and executed")
        except:
            logging.warning("plugin '"+ str(plugin) +"' failed to load and execute")
        
        

    return text

    



