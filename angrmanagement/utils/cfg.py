
import logging
from collections import defaultdict

from .edge import EdgeSort


l = logging.getLogger('utils.cfg')


def _get_branch_instr(disassembly, node):

    if len(node.out_branches) > 1:
        l.warning('_get_branch_instr(): %s has more than one out_branches. Only the first one is considered for now. '
                  'Report it to GitHub and it will be fixed.',
                  node
                  )
    if not node.out_branches:
        # huh, why is it empty?
        l.error('_get_branch_instr(): %s does not have any out branches. Please report to GitHub.', node)
        return None

    # Get the instruction address that contains the jump
    ins_addr = node.out_branches.keys()[0]

    # Get the Instruction
    try:
        instr = disassembly['instructions'][ins_addr]
    except KeyError:
        # the instruction is not found
        l.error('_get_branch_instr(): Branch instruction %#x is not found in the Disassembly instance.', ins_addr)
        return None

    return instr


def categorize_edges(disassembly, edges):
    """
    Categorize each edge.

    :param disassembly: A Disassembly analysis instance.
    :param list edges:  A list of edges.
    :return:            None
    """

    edges_by_node = defaultdict(list)

    for edge in edges:
        edges_by_node[edge.src].append(edge)

    for src_node, items in edges_by_node.iteritems():
        if len(items) == 1:
            # is it a back edge?
            edge = items[0]
            if edge.src.addr >= edge.dst.addr:
                edge.sort = EdgeSort.BACK_EDGE

        elif len(items) == 2:
            # determine which branch is true branch
            #branch_instr = _get_branch_instr(disassembly, src_node)
            #if branch_instr is not None:
            #    concrete_target = _get_explicit_branch_target(branch_instr)

            # actually, let's determine which branch is the false branch
            fallthrough = src_node.addr + src_node.size
            edge_a, edge_b = items
            if edge_a.dst.addr == fallthrough and edge_b.dst.addr != fallthrough:
                edge_a.sort = EdgeSort.FALSE_BRANCH
                edge_b.sort = EdgeSort.TRUE_BRANCH
            elif edge_a.dst.addr != fallthrough and edge_b.dst.addr == fallthrough:
                edge_a.sort = EdgeSort.TRUE_BRANCH
                edge_b.sort = EdgeSort.FALSE_BRANCH
            else:
                # huh, there are either two fall-throughs or no fall-throughs
                pass
