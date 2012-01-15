"""
:Version: 2.1
:Compatible: Yotsuba 3.0, Yotsuba 3.1, Yotsuba 4

**Kotoba** is an XML parsing module mainly using CSS selectors level 3. This module
is inspired by the well-known jQuery JavaScript library. However, unlink jQuery,
Kotoba strictedly follows the working draft of CSS selectors level 3 (W3C
proposed recomendation).
"""
import os
import re
import codecs
from sys import stdout, exc_info
from time import time
from xml.dom import minidom

from yotsuba.core import base
from yotsuba.core import graph

__scan_only__ = [
    'Kotoba',
    'DOMElement',
    'DOMElements',
    'DataElement',
    'KotobaCheckpointScreeningException',
    'KotobaGraphException',
    'KotobaInvalidSelectionException',
    'KotobaQueryException',
    'KotobaSourceException'
    ]
__version__ = 2.1

log = base.logger.getBasic("Yotsuba/Kotoba", base.logger.level.debugging)
#log = base.logger.getBasic("Yotsuba/Kotoba")
base.logger.disable()

class Kotoba(object):
    '''
    XML Parser with Level-3 CSS Selectors
    
    Currently supported selectors:
    
    * selectors with at least one of element name, attributes and pseudo classes (only ``:root`` and ``:empty``)
    * all four combinations of selectors are supported (e.g., ``selector_1 operator_1 selector_2 ...``)
    * support wildcard search (only for element name)
    * support multi combinations in a single statement (e.g., ``combo_1, combo_2``)
    '''
    def __init__(self, source = None):
        """
        Construct an XML parser using CSS3 selectors
        """
        # Attributes
        self.__xmldoc = None            # Original Document
        self.__originalReference = None # Reference to old XML object
        self.__root_element = None      # Reference to the root node
        
        if source is not None:
            self.read(source)
    
    def read(self, source):
        """
        Read the data (strictly well-formatted XML or Kotoba-compatible) from the source.
        
        Source can be a file name, XML-formatted string or DOMElement (Yotsuba 3's).
        """
        # Load XML Document as a unicode file
        if base.isString(source) and os.path.exists(source):
            fp = codecs.open(source, 'r')
            self.__xmldoc = fp.read()
            fp.close()
        # XML document as string
        elif base.isString(source) and not os.path.exists(source):
            self.__xmldoc = source
        # Assign the root document with DOMElement object
        elif source is DOMElement:
            self.__root_element = source
        # Raise exception for unknown type of source
        else:
            raise KotobaSourceException("Unknown type of source. Cannot load the data from source. (Given: %s)" % type(source))
        
        if base.isString(source):
            self.__graph()
    
    def __graph(self):
        """
        Create a graph the data from XML data.
        """
        if self.__xmldoc is None and self.__root_element is None:
            raise KotobaGraphException("Cannot make a (tree) graph as there is no XML document stored in the memory and there is not root element specified.")
        
        self.__originalReference = minidom.parseString(self.__xmldoc)
        if self.__originalReference is None:
            raise KotobaGraphException("Null pointer referred for the original reference.")
        self.__root_element = DOMElement.make(self.__originalReference.documentElement)
    
    def get(self, selector, **kwargs):
        """
        Get the element from the selector (as string or unicode). If the optional parameter root_node (as DOMElement) is given, Kotoba will use the given node as the starting point instead of the default one.
        """
        root_node        = 'root_node' in kwargs and kwargs['root_node'] or self.__root_element
        found_elements   = root_node.get(selector)
        return found_elements
    
    def get_root(self):
        '''
        Get the root element.
        '''
        return self.__root_element
    
    # Incomplete
    def __str__(self):
        """
        Get nice presentation of the tree graph with some additional information in XML format
        """
        return '<?xml version="1.0" encoding="utf-8"?><!-- Tree Graph Representation from Kotoba --><source></source>'

##### DOM and Data Elements ####################################################
class DOMElements(graph.Graph):
    '''
    Group of reference to DOM elements
    '''
    def get(self, query, **kwargs):
        '''
        Get the descendant with the query (as string or unicode) which is a valid
        CSS3 selector.

        Returns the result as DOMElements.
        '''
        original_found_elements = DOMElements()
        found_elements = DOMElements()
        
        for node in self:
            original_found_elements.extend(node.get(query))
        
        for found_element in original_found_elements:
            if found_element in found_elements:
                continue
            found_elements.append(found_element)
        
        del original_found_elements
        
        return found_elements
    
    def data(self):
        '''
        Recursively get the (text) data of all nodes in list.

        Returns as a string where the data from each node and its descendants is
        concatenated with an empty character.
        '''
        returned_data = []
        
        for node in self:
            returned_data.extend(node.data())
        
        return ''.join(returned_data)

class DOMElement(graph.Vertex):
    '''
    DOM element of the document.
    
    *name* is the name of the node.
    '''
    def __init__(self, name, **kwargs):
        self.init(name)
        self.id         = time()
        self.element    = 'reference'   in kwargs and kwargs['reference']    or None
        self.attrs      = 'attributes'  in kwargs and kwargs['attributes']   or {}
        self.level      = 'level'       in kwargs and kwargs['level']        or 0
        self.index      = 'index'       in kwargs and kwargs['index']        or 0
        self.parent_node= 'parent_node' in kwargs and kwargs['parent_node']  or None
        self.next_node  = 'next_node'   in kwargs and kwargs['next_node']    or None
        self.prev_node  = 'prev_node'   in kwargs and kwargs['prev_node']    or None
        
        if self.element is not None:
            # reference for the child node before the current node
            childNodeBeforeCurrentNode = None
            # list of nodeIDs
            nodeIDs = range(len(self.element.childNodes))
            # each node:
            for nodeID in nodeIDs:
                # reference to the child node
                rawNode = self.element.childNodes[nodeID]
                # reference to the new node
                newNode = None
                if not self.__is_XML_Data_Node(rawNode) and not self.__is_XML_Element_Node(rawNode):
                    continue
                
                if self.__is_XML_Data_Node(rawNode):
                    # create a data node
                    newNode = DataElement(rawNode.data)
                elif self.__is_XML_Element_Node(rawNode):
                    # create a DOM node
                    newNode = DOMElement.make(
                        rawNode,
                        level = self.level + 1,
                        index = nodeID,
                        parent_node = self,
                        prev_node = childNodeBeforeCurrentNode
                    )
                    # mark the current node as the previous node for the next one
                    childNodeBeforeCurrentNode = newNode
                # connect the dot
                self.make_edge_to(newNode)
            
            child_nodes = self.children()
            lastIndex = len(child_nodes) - 1
            for i in range(len(child_nodes)):
                if i < lastIndex:
                    child_nodes[i].next_node = child_nodes[i + 1]
                else:
                    pass
    
    def __is_XML_Element_Node(self, XMLNode):
        return XMLNode.nodeType == XMLNode.ELEMENT_NODE
    
    def __is_XML_Data_Node(self, XMLNode):
        return XMLNode.nodeType in (XMLNode.TEXT_NODE, XMLNode.CDATA_SECTION_NODE)
    
    @staticmethod
    def make(reference, **kwargs):
        '''
        Instantiate from an instance of XMLNode (in xml.dom.minidom). This is a static method.
        '''
        attr = {}
        if 'attributes' in dir(reference):
            for key in reference.attributes.keys():
                attr[key] = reference.getAttribute(key)
        return DOMElement(reference.tagName, attributes = attr, reference = reference, **kwargs)
    
    def get_name(self):
        '''
        Get the name of the element
        '''
        return self.name
    
    def set_name(self, new_name):
        '''
        Set the name of the element with new_name (as string or unicode).
        '''
        if base.isString(new_name):
            self.name = new_name
        return self.name
    
    def data(self, **kwargs):
        '''
        Recursively get the (text) data of all nodes in list.

        Returns as a string where the data from each node and its descendants is
        concatenated with an empty character.
        '''
        returned_data = []
        for adjacent_node in self.adjacents:
            if type(adjacent_node) is DataElement:
                returned_data.append(adjacent_node.data)
            elif type(adjacent_node) is DOMElement:
                # recursively get the data from the data node.
                returned_data.append(adjacent_node.data())
        return ''.join(returned_data)
    
    def children(self, query = None):
        '''
        Get the children of this node.

        If the optional parameter query is not provided, it will return all
        children. Otherwise, this will works like self.get, except it only looks
        for the direct descendants with the query.
        '''
        children = []
        # When there is no query, return all children
        if query is None:
            for adjacent_node in self.adjacents:
                if type(adjacent_node) is not DOMElement:
                    continue
                children.append(adjacent_node)
            return children
        # Otherwise, look by the query. Set max_depth to 1 to indicate that we are only interested in the children level.
        return self.get(query, max_depth = 1)
    
    def parent(self, new_reference = None):
        '''
        Get the parent of this node.

        If the optional parameter new_reference is provided, the current
        reference will be replaced.
        '''
        if type(new_reference) is DOMElement:
            self.parent_node = new_reference
        return self.parent_node
    
    def next(self, new_reference = None):
        '''
        Get the next node.

        If the optional parameter new_reference is provided, the current
        reference will be replaced.
        '''
        if type(new_reference) is DOMElement:
            self.next_node = new_reference
        return self.next_node
    
    def prev(self, new_reference = None):
        '''
        Get the previous node.

        If the optional parameter new_reference is provided, the current
        reference will be replaced.
        '''
        if type(new_reference) is DOMElement:
            self.prev_node = new_reference
        return self.prev_node
    
    def get(self, selector, **kwargs):
        '''
        Get the descendant with the selector (as string or unicode) which is a
        valid CSS3 selector.

        Returns the result as DOMElements.
        '''
        originalfound_elements = DOMElements()
        found_elements = DOMElements()
        
        combinators = Combinators(selector)
        
        for combinator in combinators:
            originalfound_elements.extend(self.__get(self, combinator, 0, check_origin = True, **kwargs))
        
        for foundElement in originalfound_elements:
            if foundElement in found_elements: continue
            found_elements.append(foundElement)
        
        del originalfound_elements
        
        return found_elements
    
    def __get(self, DOM_subtree, selector, index, **kwargs):
        '''
        General criteria to determine whether this is the target element.
        ------------------------------------------------------------------------
        Check if this node is matched and requires the next selector.
            If so, then
                this selector is the last selector, then
                    append the element to the list.
                Otherwise,
                    shift to the next selector.
            else,
                keep seeking for it.
        '''
        found_elements = DOMElements()
        selector_shifted = False
        check_origin = 'check_origin' in kwargs and kwargs['check_origin']

        # Check if there is force-disable-recursion signal.
        force_stop = 'force_stop' in kwargs and kwargs['force_stop']

        if index >= len(selector):
            index = len(selector) - 1
        flag = self.__CombinationMethodFlag(selector[index].combo_method)
        
        log.debug("DOMElement.__get: [BEGIN]")
        log.debug("DOMElement.__get: [INIT] Pointer:\t%s" % DOM_subtree)
        log.debug("DOMElement.__get: [INIT] Up:\t%s" % DOM_subtree.parent())
        log.debug("DOMElement.__get: [INIT] Next:\t%s" % DOM_subtree.next())
        log.debug("DOMElement.__get: [INIT] Prev:\t%s" % DOM_subtree.prev())
        log.debug("DOMElement.__get: [INIT] Use:\t%s" % selector[index])
        
        # Check if the root of this subtree is on the path
        if check_origin and self.__require_next_selector(selector[index], DOM_subtree):
            log.debug("DOMElement.__get: Check Origin > OK")

            if selector[index].end_of_query:
                log.debug("DOMElement.__get: Reached the last selector (%s)" % selector[index].name)
                found_elements.append(DOM_subtree)
                if not selector[index].is_wildcard() or (selector[index].is_wildcard() and len(DOM_subtree.children()) == 0):
                    log.debug("DOMElement.__get: Reached the last selector > Break")
                    return found_elements
                else:
                    log.debug("DOMElement.__get: Reached the last selector > Wildcard")

            if flag.look_for_descendants or flag.look_for_children:
                if not selector[index].end_of_query:
                    index += 1
                    selector_shifted = True
                    log.debug("DOMElement.__get: Check Origin > Shift the selector")
                    flag = self.__CombinationMethodFlag(selector[index].combo_method)
                    log.debug("DOMElement.__get: [RENEW] Use:\t%s" % selector[index])
            else:
                log.debug("DOMElement.__get: Check Origin > STDBY")
        
        args = {
            'selector_shifted': selector_shifted,
            'force_stop': force_stop
        }
        
        log.debug("DOMElement.__get: ARGS > %s" % args)

        if flag.look_for_descendants or flag.look_for_children:
            # CSS 1: Look for descendants
            # CSS 2: Look for children
            log.debug("DOMElement.__get: Descendant")
            child_nodes = DOM_subtree.children()
            if len(child_nodes) == 0:
                log.debug("DOMElement.__get: Descendant > Break")
            
            for node in child_nodes:
                if flag.look_for_descendants:
                    log.debug("DOMElement.__get: Descendant > All")
                else:
                    log.debug("DOMElement.__get: Descendant > Only children")

                self.__add_target_or_continue(
                    node,
                    selector,
                    index,
                    found_elements,
                    **args
                )
            
        elif flag.look_for_adjacent_siblings or flag.look_for_general_siblings:
            # CSS 2: Look for the immediate siblings (adjacent)
            # CSS 3: Look for any next siblings
            next_node = DOM_subtree.next()
            log.debug("DOMElement.__get: Sibling")
            # CASE KTB__G1: If it is not a checkpoint and the next node is not
            # available, then iterate in the deeper level.
            if not self.__require_next_selector(selector[index], DOM_subtree) and next_node is None:
                log.debug("DOMElement.__get: Sibling > Level > Next")
                for node in DOM_subtree.children():
                    self.__add_target_or_continue(
                        node,
                        selector,
                        index,
                        found_elements,
                        **args
                    )
                    
            # CASE KTB__G2: self.__add_target_or_continue handles the case "this node is the checkpoint and the next node is assigned"
            elif self.__require_next_selector(selector[index], DOM_subtree) and next_node is not None:
                log.debug("DOMElement.__get: Sibling > Level > Same")
            # CASE KTB__G3: otherwise, break!
            else:
                log.debug("DOMElement.__get: Sibling > Unhandled Case > Break")
                pass
        else:
            raise KotobaQueryException("Unknown combination method")
        log.debug("DOMElement.__get: [END]")
        
        return found_elements
    
    def __add_target_or_continue(self, reference_node, selector, index, found_elements, **kwargs):
        log.debug("DOMElement.__add_target_or_continue: [BEGIN]")
        log.debug("DOMElement.__add_target_or_continue: [INIT] Pointer:\t%s" % reference_node)
        log.debug("DOMElement.__add_target_or_continue: [INIT] Up:\t\t%s" % reference_node.parent())
        log.debug("DOMElement.__add_target_or_continue: [INIT] Next:\t%s" % reference_node.next())
        log.debug("DOMElement.__add_target_or_continue: [INIT] Prev:\t%s" % reference_node.prev())
        log.debug("DOMElement.__add_target_or_continue: [INIT] Use:\t%s" % selector[index])
        
        selector_shifted = 'selector_shifted' in kwargs and kwargs['selector_shifted']
        force_stop = 'force_stop' in kwargs and kwargs['force_stop']
        
        log.debug("DOMElement.__add_target_or_continue: [INIT] ARGS > %s" % kwargs)
        
        prev_flag_index = index
        if selector_shifted:
            log.debug("DOMElement.__add_target_or_continue: [ALERT] Selector shifted")
        prev_flag_index = index > 0 and index - 1 or 0
        
        flag = self.__CombinationMethodFlag(selector[index].combo_method)
        prev_flag = self.__CombinationMethodFlag(selector[prev_flag_index].combo_method)
        
        log.debug("DOMElement.__add_target_or_continue: [WATCH] %s" % reference_node)
        log.debug("DOMElement.__add_target_or_continue: [WATCH] %s" % selector[prev_flag_index])
        
        next_selector_required = self.__require_next_selector(selector[index], reference_node)
        local_found_elements = DOMElements()
        
        # CASE KTB__ATOKI1: If this reference node is the checkpoint
        if next_selector_required:
            proceed_to_next_rule = True
            add_reference_node = False

            log.debug("DOMElement.__add_target_or_continue: Checkpoint")
            # CASE KTB__ATOKI1_1: If this is the end of selector
            if selector[index].end_of_query:
                # Stop the iteration
                proceed_to_next_rule = False
                if not prev_flag.look_for_children or (prev_flag.look_for_children and self.__require_next_selector(selector[prev_flag_index], reference_node.parent())):
                    log.debug("DOMElement.__add_target_or_continue: Checkpoint > Add (A)")
                    add_reference_node = True
                else:
                    log.debug("DOMElement.__add_target_or_continue: Checkpoint > Break")
            
                # CASE KTB__ATOKI1_1X: Exception of ATOKI1_1 if the wildcard is the last element.
                if selector[index].is_wildcard():
                    log.debug("DOMElement.__add_target_or_continue: Checkpoint > Add (B)")
                    proceed_to_next_rule = True
                    add_reference_node = True
            
            if add_reference_node:
                local_found_elements.append(reference_node)
            
            if proceed_to_next_rule:
                # CASE KTB__G2/KTB__ATOKI1_2: Else if the selector looks for descendants
                if flag.look_for_descendants:# and not force_stop:
                    log.debug("DOMElement.__add_target_or_continue: Checkpoint > Descendants")
                    # Dig deeper and look for the next checkpoint
                    local_found_elements.extend(self.__get(reference_node, selector, index + 1))
                # CASE KTB__G2/KTB__ATOKI1_3: Else if the selector looks for children
                elif flag.look_for_children:# and not force_stop:
                    log.debug("DOMElement.__add_target_or_continue: Checkpoint > Children")
                    # Dig deeper and look for the next checkpoint
                    found_elements_from_iteration = self.__get(reference_node, selector, index + 1, force_stop = True)
                    log.debug("DOMElement.__add_target_or_continue: found elements > %d" % len(found_elements_from_iteration))
                    for __f in found_elements_from_iteration:
                        log.debug("DOMElement.__add_target_or_continue: found elements > %s > PARENT: %s" % (__f, __f.parent()))
                    local_found_elements.extend(found_elements_from_iteration)
                # CASE KTB__ATOKI1_3: Else if this is sibling search but the next node is available
                elif reference_node.next() is not None and not force_stop:
                    log.debug("DOMElement.__add_target_or_continue: Checkpoint > Sibling > Next")
                    next_node = reference_node.next()
                    while next_node is not None:
                        local_found_elements.extend(self.__get(
                            next_node,
                            selector,
                            index + 1,
                            check_origin = True
                        ))

                        if flag.look_for_adjacent_siblings:
                            log.debug("DOMElement.__add_target_or_continue: Checkpoint > Sibling > Adjacent > Break")
                            break

                        next_node = next_node.next()
                # CASE KTB__ATOKI1_4:
                else:
                    log.debug("DOMElement.__add_target_or_continue: Checkpoint > Unknown condition > break")
                    log.debug(
                        "|_ %s %s %s %s (%s)" % (
                            flag.look_for_descendants,
                            flag.look_for_children,
                            flag.look_for_general_siblings,
                            flag.look_for_adjacent_siblings,
                            force_stop
                        )
                    )
            else:
                log.debug("DOMElement.__add_target_or_continue: Checkpoint > Break by stopper conditions")
        
        found_elements.extend(local_found_elements)
        
        # CASE KTB__ATOKI2: If this reference node is not the checkpoint and it is not looking for children
        if not flag.look_for_children or (not next_selector_required and not local_found_elements):
            log.debug("DOMElement.__add_target_or_continue: Negative > All kinds of decendents")
            # Dig deeper but still look for the SAME checkpoint
            found_elements.extend(self.__get(reference_node, selector, index))
        else:
            log.debug("DOMElement.__add_target_or_continue: Ignore the node.")
        
        log.debug("DOMElement.__add_target_or_continue: [END]")
    
    def __require_next_selector(self, single_selector, reference_node = None):
        '''
        Test if the reference node is matched with the given selector.
        '''
        test_node = reference_node is None and self or reference_node
        try:
            # Check if the name of the element is the same as what the selector
            # is looking for. Bypass the check if the selector is using wildcard.
            if base.isString(single_selector.name) and not single_selector.is_wildcard():
                assert single_selector.name == test_node.name, "Expect: %s (Actual: %s)" % (single_selector.name, test_node.name)
            # @type single_selector Selector
            # @type test_node DOMElement
            #log.debug("DOMElement.__require_next_selector: Check node name > Passed (%s = %s)" % (single_selector.name, test_node.name))
            #log.debug('DOMElement.__require_next_selector: Watch > test_node.attr = %s' % test_node.attrs)
            for attr_name, attr_value in single_selector.attributes.iteritems():
                try:
                    flag_begin_with = attr_name[-1] == '^'
                    flag_end_with = attr_name[-1] == '$'
                    flag_contain_substr = attr_name[-1] == '*'
                    flag_whitespace_separated_value_partial_match = attr_name[-1] == '~'
                    flag_hyphen_separated_value_partial_match = attr_name[-1] == '|'
                    attr_name = re.sub("(\^|\$|\*|\~|\|)$", '', attr_name)

                    assert attr_name in test_node.attrs, "Missing attribute"
                    if attr_value:
                        if flag_begin_with:
                            log.debug("DOMElement.__require_next_selector: Test flag_begin_with for %s" % attr_name)
                            assert re.search("^" + attr_value, test_node.attrs[attr_name]) is not None
                        elif flag_end_with:
                            log.debug("DOMElement.__require_next_selector: Test flag_end_with for %s" % attr_name)
                            assert re.search(attr_value + "$", test_node.attrs[attr_name]) is not None
                        elif flag_contain_substr:
                            log.debug("DOMElement.__require_next_selector: Test flag_contain_substr for %s" % attr_name)
                            assert re.search(attr_value, test_node.attrs[attr_name]) is not None
                        elif flag_hyphen_separated_value_partial_match:
                            log.debug("DOMElement.__require_next_selector: Test flag_whitespace_separated_value_partial_match for %s" % attr_name)
                            assert re.match(attr_value + "-?", test_node.attrs[attr_name]) is not None or re.search("^" + attr_value + "-", test_node.attrs[attr_name], re.I) is not None
                        elif flag_whitespace_separated_value_partial_match:
                            log.debug("DOMElement.__require_next_selector: Test flag_hyphen_separated_value_partial_match for %s" % attr_name)
                            keywords_found = False
                            for token in re.split(' ', test_node.attrs[attr_name]):
                                try:
                                    log.debug("DOMElement.__require_next_selector: Comparing (attr_v) %s and (token) %s " % (attr_value, token))
                                    assert token == attr_value
                                    keywords_found = True
                                except:
                                    pass # handled by keywords_found below
                                finally:
                                    if keywords_found:
                                        break
                            if not keywords_found:
                                raise KotobaCheckpointScreeningException()
                        else:
                            log.debug("DOMElement.__require_next_selector: Test for the normal operator for %s" % attr_name)
                            assert test_node.attrs[attr_name] == attr_value
                except:
                    assert False, "Unexpected error"
            for pclass in single_selector.pseudo_classes:
                log.debug("DOMElement.__require_next_selector: Pseudo class > " + pclass)
                if pclass == "root":
                    assert test_node.level == 0
                elif pclass == "empty":
                    assert len(test_node.children()) == 0
            log.debug("DOMElement.__require_next_selector: Passed all assertions")
            return True
        except AssertionError:
            log.debug("DOMElement.__require_next_selector: Failed assertions")
            log.debug("Details: %s" % exc_info()[1])
            return False
        except:
            log.debug("Unexpected error: %s" % exc_info()[0])
            return False
    
    def identifier(self):
        ''' Text-friendly representation of the element '''
        return u'%s at %s, %s (ID = %f)' % (self.name, self.level, self.index, self.id)
    
    def hash(self):
        ''' Hash code of the element '''
        return base.hash(self.identifier())
    
    def append(self, node):
        '''
        Append a *node* of DOMElement or DataElement as the last child of this node.
        '''
        return self.make_edge_to(node)
    
    def __hash__(self):
        return self.hash()
    
    def __str__(self):
        return "DOMElement: %s" % (self.identifier())
    
    def __eq__(self, other):
        return self.hash() == other.hash()
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def to_xml(self, is_from_recursion=False, encoding="utf-8"):
        output = ['<?xml version="1.0" encoding="%s"?>' % encoding]
        if is_from_recursion:
            output = []
        glue = ''
        
        # Open tag
        output.append('<%s' % self.name)
        for attr_k, attr_v in self.attrs.iteritems():
            output.append(' %s="%s"' % (attr_k, attr_v))
        output.append('>')
        
        # Content under this node
        for adjacent_node in self.adjacents:
            if type(adjacent_node) is DataElement:
                output.append(adjacent_node.data)
            elif type(adjacent_node) is DOMElement:
                # recursively get the data from the data node.
                output.append(adjacent_node.to_xml(True))
        
        # Close tag
        output.append('</%s>' % self.name)
        return glue.join(output)
    
    class __CombinationMethodFlag(object):
        def __init__(self, combo_method):
            self.look_for_descendants         = combo_method == Selector.look_for_descendants
            self.look_for_children            = combo_method == Selector.look_for_children
            self.look_for_adjacent_siblings    = combo_method == Selector.look_for_adjacent_siblings
            self.look_for_general_siblings     = combo_method == Selector.look_for_general_siblings
        
        def __str__(self):
            return 'Flag: %s %s %s %s' % (self.look_for_descendants, self.look_for_children, self.look_for_adjacent_siblings, self.look_for_general_siblings)

class DataElement(graph.Vertex):
    """ Data structure representing a data block in an XML document """
    def __init__(self, data_string):
        '''
        Data Element (data block) in an XML document
        '''
        self.init("yotsuba.Kotoba.DataElement")
        self.data = data_string.strip()
        
    def __str__(self):
        return "DataElement: %s" % self.data

##### Selectors and Selection Combinators ######################################
class Combinators(list):
    def __init__(self, combinators = None):
        '''
        Multiple selection combinators
        '''
        self.combinators = combinators
        if combinators is not None:
            self.init(combinators)
    
    def init(self, combinators):
        # Check type
        if not base.isString(combinators):
            raise KotobaInvalidSelection("Not a string")
        
        self.combinators = combinators
        
        # Prepare data
        raw_combinators = base.convertToUnicode(combinators)
        raw_combinators = re.split("\s*,\s*", raw_combinators.strip())
        
        for raw_combinator in raw_combinators:
            if raw_combinator == '':
                raise KotobaInvalidSelectionException("Invalid multiple combinators. Perhaps there is a leading/tailing comma or an empty combinator/selector.")
            combinator = Combinator(raw_combinator)
            self.append(combinator)

class Combinator(list):
    def __init__(self, combinator=None):
        '''
        A single selection combinator
        
        Note that *combinator* is a combination set of selectors and *combiner*
        in the given order.
        
        A *combiner* is a character, such as >, + and ~, which implies how the
        currently referred selector relates to the next selector.
        '''
        self.combinator = combinator
        if combinator is not None:
            self.init(combinator)
    
    def __str__(self):
        return "Selection Combinator: %(combinator)s" % {
            'combinator': self.combinator
        }
    
    def init(self, combinator):
        # Check type
        if not base.isString(combinator):
            raise KotobaInvalidSelectionException("Not a string")
        
        self.combinator = combinator
        
        # Check for invalid combinator (part 1: not start or end with combining instruction)
        if re.search("^(>|\+|~)", combinator) or re.search("(>|\+|~)$", combinator):
            raise KotobaInvalidSelectionException("Not start or end with combining instruction (>, +, ~)")
        
        # Prepare data
        raw_combinator = base.convertToUnicode(combinator)
        raw_combinator = re.split("\s+", raw_combinator.strip())
        
        # Local buffer
        raise_on_next_combiner = False
        
        # Note: at this point, there is no combiners leading or tailing the combinator.
        for combo_block in raw_combinator:
            if combo_block in Selector.combination_map.keys():
                # [If it is a registered combiner]
                if not raise_on_next_combiner:
                    raise_on_next_combiner = True
                    self[-1].combo_method = Selector.combination_map[combo_block]
                    log.debug("Combinator.init: Reset the iteration method of the last selector (%s) to %s" % (self[-1].name, self[-1].combo_method))
                else:
                    raise KotobaInvalidSelectionException("No consecutive combiners allowed")
            else:
                # [Not registered combiner]
                raise_on_next_combiner = False
                
                selector = Selector(combo_block)
                self.append(selector)
                #print "Combinators >> init >> combo not registered"
                #print self[-1]
        self[-1].end_of_query = True

class Selector(object):
    # Reserved pseudo class
    reserved_pseudo_class       = [':root', ':empty']
    # Type of combination
    look_for_descendants        = 0
    look_for_children           = 1
    look_for_adjacent_siblings  = 2
    look_for_general_siblings   = 3
    combination_map = {
        '>': look_for_children,
        '+': look_for_adjacent_siblings,
        '~': look_for_general_siblings
    }
    
    def __init__(self, selector, combo_method=look_for_descendants):
        '''
        A single selector
        '''
        self.selector = selector
        self.end_of_query = False    # default: False
        self.name = None             # default: wildcard
        self.pseudo_classes = []     # default: empty list
        self.attributes = {}         # default: empty hash
        self.combo_method = combo_method # default: 0
        
        # Extract the attributes from the selector
        __attrs = re.findall("\[[^\]]+\]", selector)
        for __a in __attrs:
            __attr = __a[1:-1].split("=", 2)
            self.attributes[__attr[0]] = len(__attr) > 1 and __attr[1] or None
            selector = selector.replace(__a, '')
        
        # Extract the pseudo classes from the selector
        __pclasses = re.findall(":[^:]+", selector)
        for __p in __pclasses:
            if __p not in self.reserved_pseudo_class: continue
            self.pseudo_classes.append(__p[1:])
            __pclasses.pop(__pclasses.index(__p))
            selector = selector.replace(__p, '')
        
        # Extract the target element name from the selector
        if selector == '' or selector == '*':
            pass # wildcard selector
        elif len(selector) > 1 and '*' in selector:
            raise KotobaInvalidSelectionException("Multiple wildcard characters not allowed")
        else:
            self.name = selector

    def is_wildcard(self):
        return self.name is None

    def __str__(self):
        output = "Selector: %s" % self.selector
        
        if self.combo_method == self.look_for_children:
            output += "; Inst: Only look for children"
        elif self.combo_method == self.look_for_adjacent_siblings:
            output += "; Inst: Only look for adjacent siblings"
        elif self.combo_method == self.look_for_general_siblings:
            output += "; Inst: Only look for all siblings"
        
        if len(self.attributes) > 0:
            output += "; Attr: %s" % unicode(self.attributes)
        
        if len(self.pseudo_classes) > 0:
            output += "; Pcls: %s" % unicode(self.pseudo_classes)
        
        return output

##### Exceptions ###############################################################
class KotobaSourceException(Exception):
    '''
    Exception for invalid source when Kotoba reads the source. The source may be
    neither supported data type (string or *kotoba.DOMElement*) nor existed file.
    '''
    __scan_only__ = []

class KotobaGraphException(Exception):
    '''
    Exception when Kotaba cannot create a graph from the source. See the
    documentation for *xml.dom.minidom* (Python's built-in module) for more
    information on the supported formats.
    '''
    __scan_only__ = []

class KotobaQueryException(Exception):
    '''
    Exception for error during iteration. This is a *critical* error.
    '''
    __scan_only__ = []

class KotobaInvalidSelectionException(Exception):
    '''
    Exception for invalid selector. See the W3C document on level-3 CSS selector
    and the documentation of what *kotoba.Kotoba* supports.
    '''
    __scan_only__ = []

class KotobaCheckpointScreeningException(Exception):
    '''
    Exception for failing a series of assertions when Kotoba tries to determine
    whether Kotoba requires to proceed the current iteration. If this error is
    thrown, it is definitely a bug.
    '''
    __scan_only__ = []
