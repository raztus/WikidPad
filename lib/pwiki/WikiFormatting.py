from Enum import Enumeration
# from Config import faces

import srePersistent as re


FormatTypes = Enumeration("FormatTypes", ["Default", "WikiWord2", "WikiWord", "AvailWikiWord",                                          
                                          "Bold", "Italic", "Heading4", "Heading3", "Heading2", "Heading1",
                                          "Url", "Script", "Property", "ToDo",
                                          "HorizLine", "Bullet", "Numeric",
                                          "Suppress"], 1)

def initialize(wikiSyntax):
    import WikiFormatting as ownmodule
    for item in dir(wikiSyntax):
        if item.startswith("_"):   # TODO check if necessary
            continue
        setattr(ownmodule, item, getattr(wikiSyntax, item))

    
    global FormatExpressions
    global CombinedSyntaxHighlightWithCamelCaseRE
    global CombinedSyntaxHighlightWithoutCamelCaseRE
    global UpdateExpressions
    global CombinedUpdateWithCamelCaseRE
    global CombinedUpdateWithoutCamelCaseRE
    global HtmlExportExpressions
    global CombinedHtmlExportWithCamelCaseRE
    global CombinedHtmlExportWithoutCamelCaseRE

# Reordered version, most specific first

    FormatExpressions = [
            (SuppressHighlightingRE, FormatTypes.Default),
            (ScriptRE, FormatTypes.Script),
            (UrlRE, FormatTypes.Url),
            (ToDoRE, FormatTypes.ToDo),
            (PropertyRE, FormatTypes.Property),
            (FootnoteRE, FormatTypes.Default),
            (WikiWordEditorRE2, FormatTypes.WikiWord2),
            (WikiWordEditorRE, FormatTypes.WikiWord),
            (BoldRE, FormatTypes.Bold),
            (ItalicRE, FormatTypes.Italic),
            (Heading4RE, FormatTypes.Heading4),
            (Heading3RE, FormatTypes.Heading3),
            (Heading2RE, FormatTypes.Heading2),
            (Heading1RE, FormatTypes.Heading1)
            ]

    # Build combined regexps
    WithCamelCase = []
    WithoutCamelCase = []
    for i in range(len(FormatExpressions)):
        r, s = FormatExpressions[i]
#     for r, s in FormatExpressions:
        WithCamelCase.append((u"(?P<style%i>" % i) + r.pattern + u")")
        if not s is FormatTypes.WikiWord:
            WithoutCamelCase.append((u"(?P<style%i>" % i) + r.pattern + u")")


    CombinedSyntaxHighlightWithCamelCaseRE = \
            re.compile(u"|".join(WithCamelCase),
                    re.DOTALL | re.UNICODE | re.MULTILINE)
    CombinedSyntaxHighlightWithoutCamelCaseRE = \
            re.compile(u"|".join(WithoutCamelCase),
                    re.DOTALL | re.UNICODE | re.MULTILINE)
    

    UpdateExpressions = [
            (SuppressHighlightingRE, FormatTypes.Default),
            (ScriptRE, FormatTypes.Script),
            (UrlRE, FormatTypes.Url),
            (ToDoREWithContent, FormatTypes.ToDo),
            (PropertyRE, FormatTypes.Property),
            (FootnoteRE, FormatTypes.Default),
            (WikiWordRE2, FormatTypes.WikiWord2),
            (WikiWordRE, FormatTypes.WikiWord),
            ]

    # Build combined regexps
    WithCamelCase = []
    WithoutCamelCase = []
    for i in range(len(UpdateExpressions)):
        r, s = UpdateExpressions[i]
#     for r, s in FormatExpressions:
        WithCamelCase.append((u"(?P<style%i>" % i) + r.pattern + u")")
        if not s is FormatTypes.WikiWord:
            WithoutCamelCase.append((u"(?P<style%i>" % i) + r.pattern + u")")

    CombinedUpdateWithCamelCaseRE = \
            re.compile(u"|".join(WithCamelCase),
                    re.DOTALL | re.UNICODE | re.MULTILINE)
    CombinedUpdateWithoutCamelCaseRE = \
            re.compile(u"|".join(WithoutCamelCase),
                    re.DOTALL | re.UNICODE | re.MULTILINE)


    HtmlExportExpressions = [
            (SuppressHighlightingRE, FormatTypes.Suppress),
            (ScriptRE, FormatTypes.Script),
            (UrlRE, FormatTypes.Url),
            (ToDoREWithContent, FormatTypes.ToDo),
            (PropertyRE, FormatTypes.Property),
            (FootnoteRE, FormatTypes.Default),
            (WikiWordRE2, FormatTypes.WikiWord2),
            (WikiWordRE, FormatTypes.WikiWord),
            (BoldRE, FormatTypes.Bold),
            (ItalicRE, FormatTypes.Italic),
            (Heading4RE, FormatTypes.Heading4),
            (Heading3RE, FormatTypes.Heading3),
            (Heading2RE, FormatTypes.Heading2),
            (Heading1RE, FormatTypes.Heading1),
            (HorizLineRE, FormatTypes.HorizLine),
            (BulletRE, FormatTypes.Bullet),
            (NumericBulletRE, FormatTypes.Numeric)
            ]
            
    # Build combined regexps
    WithCamelCase = []
    WithoutCamelCase = []
    for i in range(len(HtmlExportExpressions)):
        r, s = HtmlExportExpressions[i]
#     for r, s in FormatExpressions:
        WithCamelCase.append((u"(?P<style%i>" % i) + r.pattern + u")")
        if not s is FormatTypes.WikiWord:
            WithoutCamelCase.append((u"(?P<style%i>" % i) + r.pattern + u")")

    CombinedHtmlExportWithCamelCaseRE = \
            re.compile(u"|".join(WithCamelCase),
                    re.DOTALL | re.UNICODE | re.MULTILINE)
    CombinedHtmlExportWithoutCamelCaseRE = \
            re.compile(u"|".join(WithoutCamelCase),
                    re.DOTALL | re.UNICODE | re.MULTILINE)




def getStyles(styleFaces):
    return [(FormatTypes.Default, "face:%(mono)s,size:%(size)d" % styleFaces),
            (FormatTypes.WikiWord, "fore:#000000,underline,face:%(mono)s,size:%(size)d" % styleFaces),      
            (FormatTypes.AvailWikiWord, "fore:#0000BB,underline,face:%(mono)s,size:%(size)d" % styleFaces),      
            (FormatTypes.Bold, "bold,face:%(mono)s,size:%(size)d" % styleFaces),   
            (FormatTypes.Italic, "italic,face:%(mono)s,size:%(size)d" % styleFaces), 
            (FormatTypes.Heading4, "bold,face:%(mono)s,size:%(heading4)d" % styleFaces),       
            (FormatTypes.Heading3, "bold,face:%(mono)s,size:%(heading3)d" % styleFaces),       
            (FormatTypes.Heading2, "bold,face:%(mono)s,size:%(heading2)d" % styleFaces),       
            (FormatTypes.Heading1, "bold,face:%(mono)s,size:%(heading1)d" % styleFaces), 
            (FormatTypes.Url, "fore:#0000BB,underline,face:%(mono)s,size:%(size)d" % styleFaces), 
            (FormatTypes.Script, "fore:#555555,face:%(mono)s,size:%(size)d" % styleFaces),
            (FormatTypes.Property, "bold,fore:#555555,face:%(mono)s,size:%(size)d" % styleFaces),
            (FormatTypes.ToDo, "bold,face:%(mono)s,size:%(size)d" % styleFaces)]

def isWikiWord(word):
    """
    Test if word is syntactically a wiki word
    """
    return WikiWordRE.match(word) or (WikiWordRE2.match(word) and not \
            FootnoteRE.match(word))
 

def normalizeWikiWord(word):
    """
    Try to normalize text to a valid wiki word and return it or None
    if it can't be normalized.
    """
    if WikiWordRE.match(word):
        return word
        
    if FootnoteRE.match(word):
        return None
        
    if WikiWordRE2.match(word):
        if WikiWordRE.match(word[1:-1]):
            # If word is '[WikiWord]', return 'WikiWord' instead
            return word[1:-1]
        else:
            return word
    
    # No valid wiki word -> try to add brackets
    if WikiWordRE2.match(u"[%s]" % word):
        return u"[%s]" % word
            
    return None





    
