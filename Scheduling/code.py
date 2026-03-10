from ortools.sat.python import cp_model
from openpyxl import Workbook

# -------------------------------
# Callback : affichage JOURS en LIGNES, EMPLOYÉS en COLONNES
# -------------------------------
class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, shift, num_employees, num_days, activities, limit=5):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shift = shift
        self._num_employees = num_employees
        self._num_days = num_days
        self._activities = activities
        self._solution_count = 0
        self._solution_limit = limit

    def on_solution_callback(self):
        self._solution_count += 1
        print(f"\n{'='*60}")
        print(f"✅ Solution {self._solution_count}")
        print(f"{'='*60}")

        # En-tête : employés
        header = "Jour    |"
        for e in range(self._num_employees):
            header += f" Emp{e:2} |"
        print(header)
        print("-" * len(header))

        # Lignes : un jour par ligne
        for d in range(self._num_days):
            line = f"Jour {d:2} |"
            for e in range(self._num_employees):
                val = self.Value(self._shift[e, d])
                if val == ACTIVITY_OFF:
                    act = "   "  # case vide ou "X  "
                else:
                    # Prendre les 3 premières lettres de l'activité
                    act = self._activities[val][:3]
                line += f" {act:3} |"
            print(line)

        # Optionnel : résumé du nombre de jours travaillés par employé
        print("\nRésumé (jours travaillés par employé) :")
        summary = ""
        for e in range(self._num_employees):
            worked = sum(1 for d in range(self._num_days) if self.Value(self._shift[e, d]) != ACTIVITY_OFF)
            summary += f"Emp{e}: {worked:2}j  "
        print(summary)

        if self._solution_count >= self._solution_limit:
            self.StopSearch()

    def solution_count(self):
        return self._solution_count

num_employees = 15
num_weeks = 4
days_per_week = 5
num_days = num_weeks * days_per_week
activities = ["Téléphone", "Renseignement", "Dérogation", "Réclamation", "Impayés"]
num_activities = len(activities)
ACTIVITY_OFF = -1

# congés
days_off = {
    0: [0],
    1: [5, 6],
    2: [11, 12],
    6: [1],
    8: [3],
}

model = cp_model.CpModel()

# Variables
shift = {}
for e in range(num_employees):
    for d in range(num_days):
        if d in days_off.get(e, []):
            shift[e, d] = model.NewIntVar(ACTIVITY_OFF, ACTIVITY_OFF, f'shift_{e}_{d}')
        else:
            shift[e, d] = model.NewIntVar(0, num_activities - 1, f'shift_{e}_{d}')

# for e in range(num_employees):
#     for d in range(num_days):
#         if d not in days_off.get(e, []):
#             # Il n'est pas en congé → il DOIT travailler ce jour
#             model.Add(shift[e, d] != ACTIVITY_OFF)

# Booléens is_assigned
is_assigned = {}
for e in range(num_employees):
    for d in range(num_days):
        for a in range(num_activities):
            b = model.NewBoolVar(f'is_{e}_{d}_{a}')
            is_assigned[e, d, a] = b
            model.Add(shift[e, d] == a).OnlyEnforceIf(b)
            model.Add(shift[e, d] != a).OnlyEnforceIf(b.Not())

# Contraintes quotidiennes
for d in range(num_days):
    model.Add(sum(is_assigned[e, d, 0] for e in range(num_employees)) >= 5)   # Téléphone
    model.Add(sum(is_assigned[e, d, 1] for e in range(num_employees)) >= 3)   # Renseignement
    for a in [2, 3, 4]:
        model.Add(sum(is_assigned[e, d, a] for e in range(num_employees)) >= 1)

# -------------------------------
# Contraintes hebdomadaires par employé (CORRIGÉES)
# -------------------------------
for e in range(num_employees):
    for w in range(num_weeks):
        days_in_week = list(range(w * days_per_week, (w + 1) * days_per_week))

        # Booléens : travaille-t-il ce jour ?
        worked_bools = []
        for d in days_in_week:
            b = model.NewBoolVar(f'worked_{e}_{w}_{d}')
            model.Add(shift[e, d] != ACTIVITY_OFF).OnlyEnforceIf(b)
            model.Add(shift[e, d] == ACTIVITY_OFF).OnlyEnforceIf(b.Not())
            worked_bools.append(b)

        worked_days = model.NewIntVar(0, days_per_week, f'total_worked_{e}_{w}')
        model.Add(worked_days == sum(worked_bools))

        # Compter les activités cette semaine
        act_counts = {}
        for a in range(num_activities):
            count_var = model.NewIntVar(0, days_per_week, f'act_count_{e}_{w}_{a}')
            model.Add(count_var == sum(is_assigned[e, d, a] for d in days_in_week))
            act_counts[a] = count_var

        # Contraintes MAX par activité (inchangées)
        model.Add(act_counts[0] <= 2)  # Téléphone
        model.Add(act_counts[1] <= 2)  # Renseignement
        model.Add(act_counts[2] <= 1)  # Dérogation
        model.Add(act_counts[3] <= 1)  # Réclamation
        model.Add(act_counts[4] <= 1)  # Impayés

        # ---- NOUVEAU : contrainte conditionnelle ----
        # Si worked_days >= 3, alors num_diff_activities >= 3
        works_at_least_3 = model.NewBoolVar(f'works_ge3_{e}_{w}')
        model.Add(worked_days >= 3).OnlyEnforceIf(works_at_least_3)
        model.Add(worked_days <= 2).OnlyEnforceIf(works_at_least_3.Not())

        # Compter le nombre d'activités différentes
        diff_act_bools = []
        for a in range(num_activities):
            b = model.NewBoolVar(f'has_act_{e}_{w}_{a}')
            model.Add(act_counts[a] >= 1).OnlyEnforceIf(b)
            model.Add(act_counts[a] == 0).OnlyEnforceIf(b.Not())
            diff_act_bools.append(b)
        num_diff = model.NewIntVar(0, num_activities, f'num_diff_{e}_{w}')
        model.Add(num_diff == sum(diff_act_bools))

        # Implication : works_at_least_3 → num_diff >= 3
        # Ce qui équivaut à : num_diff >= 3 OU worked_days <= 2
        # On l'exprime en forçant : si works_at_least_3, alors num_diff >= 3
        model.Add(num_diff >= 3).OnlyEnforceIf(works_at_least_3)
        # (Si works_at_least_3 est faux, aucune contrainte sur num_diff)

# Résolution simple
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 20.0
solver.parameters.num_search_workers = 8
# solver.parameters.enumerate_all_solutions = True
solution_printer = SolutionPrinter(shift, num_employees, num_days, activities, limit=5)
solver.SearchForAllSolutions(model, solution_printer)
status = solver.Solve(model)

wb = Workbook()
sheet = wb.active
sheet.title = "Planning"

if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
    print("✅ Solution trouvée !")
    # Afficher un extrait
    for e in range(15):  # 3 premiers employés
        sheet.cell(row = 1, column = e + 1, value = chr(65 + e))
        print(f"Employé {e:2}: ", end="")
        for d in range(20):  # première semaine
            val = solver.Value(shift[e, d])
            act = " X " if val == -1 else activities[val][:3]
            print(act, end=" ")
        print()
    wb.save('Planning.xlsx')

else:
    print("❌ Aucune solution. Le modèle est trop contraint.")


# -------------------------------
# Résolution
# -------------------------------
# solver = cp_model.CpSolver()
# solver.parameters.max_time_in_seconds = 30.0
# solver.parameters.num_search_workers = 8

# solution_printer = SolutionPrinter(shift, num_employees, num_days, activities, limit=5)
# solver.SearchForAllSolutions(model, solution_printer)

# print(f"\n✅ Nombre total de solutions affichées : {solution_printer.solution_count()}")