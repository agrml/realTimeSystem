import xml.etree.ElementTree as ET
from copy import deepcopy


class Component:
    def __init__(self, num=0.0, rel=0.0, cost=0.0):
        self.num = num
        self.rel = rel
        self.cost = cost


class Combo:
    def __init__(self, combo):
        self.combo = combo
        self.cost = 0
        self.rel = 0
        for elem in combo:
            self.cost += elem.cost
            self.rel += elem.rel


def get_not_the_worsts(components):
    res = []
    for component in components:
        cost = float(component.attrib["cost"])
        rel = float(component.attrib["rel"])
        num = float(component.attrib["num"])
        skip = False
        for item in res:
            if rel < item.rel and cost >= item.cost:
                skip = True
        if skip:
            continue
        res.append(Component(num, rel, cost))
    return res


def get_all_combinations(combinations, combo):
    if len(combo) == len(combinations):
        return combo
    l = []
    for elem in combinations[len(combo)]:
        new_combo = combo.copy()
        new_combo.append(elem)
        l.append(get_all_combinations(combinations, new_combo))
    return l


def main():
    # parse to IR and delete the worsts
    tree = ET.parse("example.xml")
    root = tree.getroot()
    limit_cost = float(root.attrib['limitcost'])
    modules = []
    for module in root:
        # components are sorted over their numbers
        sws = get_not_the_worsts(module.findall("sw"))
        hws = get_not_the_worsts(module.findall("hw"))
        modules.append([sws, hws])

    combinations = []
    for sws, hws in modules:
        # get all combinations of software and hardware components in the module
        m_combinations = []
        for sw in sws:
            for hw in hws:
                m_combinations.append([sw, hw])
        combinations.append(m_combinations)
    combinations = get_all_combinations(combinations, [])

    best_combo = None
    for combo in combinations:
        combo = Combo(combo)
        if combo.combo > limit_cost:
            continue
        if best_combo is None or combo.rel > best_combo.rel:
            best_combo = combo

    with open("result.xml", "w") as f:
        print('<system limitcost="180">', file=f)
        for idx, elem in enumerate(best_combo):
            print('\t<module num="{}">'.format(idx + 1), file=f)
            print('\t\t<sw num="{}" rel="{}" cost="{}"/>'.format(elem[0].num, elem[0].rel, elem[0].cost), file=f)
            print('\t\t<hw num="{}" rel="{}" cost="{}"/>'.format(elem[1].num, elem[1].rel, elem[1].cost), file=f)
            print('\t</module">', file=f)
        print('</system>', file=f)


if __name__ == "__main__":
    main()