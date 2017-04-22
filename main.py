import copy
import xml.etree.ElementTree as ET


class Component:
    def __init__(self, num=0.0, rel=0.0, cost=0.0):
        self.num = num
        self.rel = rel
        self.cost = cost


class Combo:
    def __init__(self, combo):
        self.combo = copy.copy(combo)
        self.cost = 0
        self.rel = 1
        for elem in combo:
            for component in elem:
                self.cost += component.cost
                self.rel *= component.rel


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
                break
        if skip:
            continue
        res.append(Component(num, rel, cost))
    return res


"""
Iterates over all combinations of in-module combinations of components
"""
class Process:
    def __init__(self, modules, limit_cost):
        self.resulting_combo = [None for i in modules]
        self.modules = modules
        self.limit_cost = limit_cost
        self.n_iter = 0
        self.best_combo = None
    
    def start(self):
        self.process(0)
        
    def process(self, depth):
        if depth < len(self.resulting_combo):
            for combo in self.modules[depth]:
                self.resulting_combo[depth] = combo
                self.process(depth + 1)
        else:
            combo = Combo(self.resulting_combo)
            self.n_iter += 1
            if combo.cost <= self.limit_cost and (self.best_combo is None or combo.rel > self.best_combo.rel):
                self.best_combo = combo

        if depth == 0:
            print(self.best_combo.cost)

            cost_check = 0
            for elem in self.best_combo.combo:
                cost_check += elem[0].cost
                cost_check += elem[1].cost
            if cost_check > 180:
                raise BaseException
            if cost_check != self.best_combo.cost:
                raise BaseException



def main():
    # parse to IR and delete the worsts
    tree = ET.parse("example.xml")
    root = tree.getroot()
    limit_cost = float(root.attrib['limitcost'])
    modules = []
    # get all not the worst software and hardware components sorted over their numbers
    for module in root:
        sws = get_not_the_worsts(module.findall("sw"))
        hws = get_not_the_worsts(module.findall("hw"))
        modules.append([sws, hws])

    # get all combinations of software and hardware components for every module
    combinations_by_modules = []
    for sws, hws in modules:
        m_combinations = []
        for sw in sws:
            for hw in hws:
                m_combinations.append([sw, hw])
        combinations_by_modules.append(m_combinations)

    process = Process(combinations_by_modules, limit_cost)
    process.start()

    with open("result.xml", "w") as f:
        print('<system limitcost="{}" rel="{:.3f}" cost="{:.0f}" iteration="{}">'.format(
            limit_cost, process.best_combo.rel, process.best_combo.cost, process.n_iter), file=f)
        if process.best_combo is None:
            print("Error: there is no system configuration for that cost limit", file=f)
        else:
            for idx, elem in enumerate(process.best_combo.combo):
                print('\t<module num="{}">'.format(idx + 1), file=f)
                print('\t\t<sw num="{:.0f}" rel="{:.3f}" cost="{:.0f}"/>'.format(elem[0].num, elem[0].rel, elem[0].cost), file=f)
                print('\t\t<hw num="{:.0f}" rel="{:.3f}" cost="{:.0f}"/>'.format(elem[1].num, elem[1].rel, elem[1].cost), file=f)
                print('\t</module>', file=f)
        print('</system>', file=f)


if __name__ == "__main__":
    main()