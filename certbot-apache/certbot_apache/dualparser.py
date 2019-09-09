""" Tests for ParserNode interface """
from certbot_apache import assertions
from certbot_apache import augeasparser


class DualNodeBase(object):
    """ Dual parser interface for in development testing. This is used as the
    base class for dual parser interface classes. This class handles runtime
    attribute value assertions."""

    def save(self, msg):  # pragma: no cover
        """ Call save for both parsers """
        self.primary.save(msg)
        self.secondary.save(msg)

    def __getattr__(self, aname):
        """ Attribute value assertion """
        firstval = getattr(self.primary, aname)
        secondval = getattr(self.secondary, aname)
        if not assertions.isPass(firstval, secondval):
            assertions.assertSimple(firstval, secondval)
        return firstval


class DualCommentNode(DualNodeBase):
    """ Dual parser implementation of CommentNode interface """

    def __init__(self, **kwargs):
        """ This initialization implementation allows ordinary initialization
        of CommentNode objects as well as creating a DualCommentNode object
        using precreated or fetched CommentNode objects if provided as optional
        arguments primary and secondary.

        Parameters other than the following are from interfaces.CommentNode:

        :param CommentNode primary: Primary pre-created CommentNode, mainly
            used when creating new DualParser nodes using add_* methods.
        :param CommentNode secondary: Secondary pre-created CommentNode
        """

        kwargs.setdefault("primary", None)
        kwargs.setdefault("secondary", None)
        primary = kwargs.pop("primary")
        secondary = kwargs.pop("secondary")

        if not primary:
            self.primary = augeasparser.AugeasCommentNode(**kwargs)
        else:
            self.primary = primary
        if not secondary:
            self.secondary = augeasparser.AugeasCommentNode(**kwargs)
        else:
            self.secondary = secondary

        assertions.assertEqual(self.primary, self.secondary)


class DualDirectiveNode(DualNodeBase):
    """ Dual parser implementation of DirectiveNode interface """

    def __init__(self, **kwargs):
        """ This initialization implementation allows ordinary initialization
        of DirectiveNode objects as well as creating a DualDirectiveNode object
        using precreated or fetched DirectiveNode objects if provided as optional
        arguments primary and secondary.

        Parameters other than the following are from interfaces.DirectiveNode:

        :param DirectiveNode primary: Primary pre-created DirectiveNode, mainly
            used when creating new DualParser nodes using add_* methods.
        :param DirectiveNode secondary: Secondary pre-created DirectiveNode


        """

        kwargs.setdefault("primary", None)
        kwargs.setdefault("secondary", None)
        primary = kwargs.pop("primary")
        secondary = kwargs.pop("secondary")

        if not primary:
            self.primary = augeasparser.AugeasDirectiveNode(**kwargs)
        else:
            self.primary = primary

        if not secondary:
            self.secondary = augeasparser.AugeasDirectiveNode(**kwargs)
        else:
            self.secondary = secondary

        assertions.assertEqual(self.primary, self.secondary)

    def set_parameters(self, parameters):
        """ Sets parameters and asserts that both implementation successfully
        set the parameter sequence """

        self.primary.set_parameters(parameters)
        self.secondary.set_parameters(parameters)
        assertions.assertEqual(self.primary, self.secondary)


class DualBlockNode(DualDirectiveNode):
    """ Dual parser implementation of BlockNode interface """

    def __init__(self, **kwargs):
        """ This initialization implementation allows ordinary initialization
        of BlockNode objects as well as creating a DualBlockNode object
        using precreated or fetched BlockNode objects if provided as optional
        arguments primary and secondary.

        Parameters other than the following are from interfaces.BlockNode:

        :param BlockNode primary: Primary pre-created BlockNode, mainly
            used when creating new DualParser nodes using add_* methods.
        :param BlockNode secondary: Secondary pre-created BlockNode
        """

        kwargs.setdefault("primary", None)
        kwargs.setdefault("secondary", None)
        primary = kwargs.pop("primary")
        secondary = kwargs.pop("secondary")

        if not primary:
            self.primary = augeasparser.AugeasBlockNode(**kwargs)
        else:
            self.primary = primary

        if not secondary:
            self.secondary = augeasparser.AugeasBlockNode(**kwargs)
        else:
            self.secondary = secondary

        assertions.assertEqual(self.primary, self.secondary)

    def add_child_block(self, name, parameters=None, position=None):
        """ Creates a new child BlockNode, asserts that both implementations
        did it in a similar way, and returns a newly created DualBlockNode object
        encapsulating both of the newly created objects """

        primary_new = self.primary.add_child_block(name, parameters, position)
        secondary_new = self.secondary.add_child_block(name, parameters, position)
        assertions.assertEqual(primary_new, secondary_new)
        new_block = DualBlockNode(primary=primary_new, secondary=secondary_new)
        return new_block

    def add_child_directive(self, name, parameters=None, position=None):
        """ Creates a new child DirectiveNode, asserts that both implementations
        did it in a similar way, and returns a newly created DualDirectiveNode
        object encapsulating both of the newly created objects """

        primary_new = self.primary.add_child_directive(name, parameters, position)
        secondary_new = self.secondary.add_child_directive(name, parameters, position)
        assertions.assertEqual(primary_new, secondary_new)
        new_dir = DualDirectiveNode(primary=primary_new, secondary=secondary_new)
        return new_dir

    def add_child_comment(self, comment="", position=None):
        """ Creates a new child CommentNode, asserts that both implementations
        did it in a similar way, and returns a newly created DualCommentNode
        object encapsulating both of the newly created objects """

        primary_new = self.primary.add_child_comment(comment, position)
        secondary_new = self.secondary.add_child_comment(comment, position)
        assertions.assertEqual(primary_new, secondary_new)
        new_comment = DualCommentNode(primary=primary_new, secondary=secondary_new)
        return new_comment

    def _create_matching_list(self, primary_list, secondary_list):  # pragma: no cover
        """ Matches the list of primary_list to a list of secondary_list and
        returns a list of tuples. This is used to create results for find_
        methods. """

        matched = list()
        for p in primary_list:
            match = None
            for s in secondary_list:
                try:
                    assertions.assertEqual(p, s)
                    match = s
                except AssertionError:
                    continue
            if match:
                matched.append((p,s))
            else:
                raise AssertionError("Could not find a matching node.")
        return matched

    def find_blocks(self, name, exclude=True):  # pragma: no cover
        """
        Performs a search for BlockNodes using both implementations and does simple
        checks for results. This is built upon the assumption that unimplemented
        find_* methods return a list with a single assertion passing object.
        After the assertion, it creates a list of newly created DualBlockNode
        instances that encapsulate the pairs of returned BlockNode objects.
        """

        primary_blocks = self.primary.find_blocks(name, exclude)
        secondary_blocks = self.secondary.find_blocks(name, exclude)

        # The order of search results for Augeas implementation cannot be
        # assured.

        pass_primary = assertions.isPassNodeList(primary_blocks)
        pass_secondary = assertions.isPassNodeList(secondary_blocks)
        new_blocks = list()

        if pass_primary and pass_secondary:
            # Both unimplemented
            new_blocks.append(DualBlockNode(primary=primary_blocks[0],
                                            secondary=secondary_blocks[0]))
        elif pass_primary:
            for c in secondary_blocks:
                new_blocks.append(DualBlockNode(primary=primary_blocks[0],
                                                secondary=c))
        elif pass_secondary:
            for c in primary_blocks:
                new_blocks.append(DualBlockNode(primary=c,
                                                secondary=secondary_blocks[0]))
        else:
            assert len(primary_blocks) == len(secondary_blocks)
            matches = self._create_matching_list(primary_blocks, secondary_blocks)
            for p,s in matches:
                new_blocks.append(DualBlockNode(primary=p, secondary=s))

        return new_blocks

    def find_directives(self, name, exclude=True):  # pragma: no cover
        """
        Performs a search for DirectiveNodes using both implementations and
        checks the results. This is built upon the assumption that unimplemented
        find_* methods return a list with a single assertion passing object.
        After the assertion, it creates a list of newly created DualDirectiveNode
        instances that encapsulate the pairs of returned DirectiveNode objects.
        """
        primary_dirs = self.primary.find_directives(name, exclude)
        secondary_dirs = self.secondary.find_directives(name, exclude)

        # The order of search results for Augeas implementation cannot be
        # assured.

        pass_primary = assertions.isPassNodeList(primary_dirs)
        pass_secondary = assertions.isPassNodeList(secondary_dirs)
        new_dirs = list()

        if pass_primary and pass_secondary:
            # Both unimplemented
            new_dirs.append(DualDirectiveNode(primary=primary_dirs[0],
                                              secondary=secondary_dirs[0]))
        elif pass_primary:
            for c in secondary_dirs:
                new_dirs.append(DualDirectiveNode(primary=primary_dirs[0],
                                                  secondary=c))
        elif pass_secondary:
            for c in primary_dirs:
                new_dirs.append(DualDirectiveNode(primary=c,
                                                  secondary=secondary_dirs[0]))
        else:
            assert len(primary_dirs) == len(secondary_dirs)
            matches = self._create_matching_list(primary_dirs, secondary_dirs)
            for p,s in matches:
                new_dirs.append(DualDirectiveNode(primary=p, secondary=s))

        return new_dirs

    def find_comments(self, comment, exact=False):  # pragma: no cover
        """
        Performs a search for CommentNodes using both implementations and
        checks the results. This is built upon the assumption that unimplemented
        find_* methods return a list with a single assertion passing object.
        After the assertion, it creates a list of newly created DualCommentNode
        instances that encapsulate the pairs of returned CommentNode objects.
        """
        primary_com = self.primary.find_comments(comment, exact)
        secondary_com = self.secondary.find_comments(comment, exact)

        # The order of search results for Augeas implementation cannot be
        # assured.

        pass_primary = assertions.isPassNodeList(primary_com)
        pass_secondary = assertions.isPassNodeList(secondary_com)
        new_com = list()

        if pass_primary and pass_secondary:
            # Both unimplemented
            new_com.append(DualCommentNode(primary=primary_com[0],
                                           secondary=secondary_com[0]))
        elif pass_primary:
            for c in secondary_com:
                new_com.append(DualCommentNode(primary=primary_com[0],
                                               secondary=c))
        elif pass_secondary:
            for c in primary_com:
                new_com.append(DualCommentNode(primary=c,
                                               secondary=secondary_com[0]))
        else:
            assert len(primary_com) == len(secondary_com)
            matches = self._create_matching_list(primary_com, secondary_com)
            for p,s in matches:
                new_com.append(DualCommentNode(primary=p, secondary=s))

        return new_com

    def delete_child(self, child):  # pragma: no cover
        """Deletes a child from the ParserNode implementations. The actual
        ParserNode implementations are used here directly in order to be able
        to match a child to the list of children."""

        self.primary.delete_child(child.primary)
        self.secondary.delete_child(child.secondary)

    def unsaved_files(self):
        """ Fetches the list of unsaved file paths and asserts that the lists
        match """
        primary_files = self.primary.unsaved_files()
        secondary_files = self.secondary.unsaved_files()
        assertions.assertSimple(primary_files, secondary_files)

        return primary_files