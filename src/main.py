import pandas as pd
import taipy.gui.builder as tgb
from taipy.gui import Gui

###########################################################
###                      Variables                      ###
###########################################################

# Surface
surface = 0
surface_unit = "ha"
surface_choices = ["ha", "m2 - sqm", "acres"]

# Fertilizing Requirements
field_requirement_N = 0
field_requirement_P = 0
field_requirement_K = 0

# Fertilizer products
df_fertilizer_products = pd.read_csv(
    "./src/data/inorganic_fertilizers_npk_value.csv", index_col="Fertilizer"
)
fertilizer_list = list(df_fertilizer_products.index)

fertilizer_product = "Ammonium Nitrate phosphate"  # Index 0


def select_fertilizer(fertilizer_product):
    # Composition
    fertilizer_composition_N = int(df_fertilizer_products.loc[fertilizer_product, "N"])
    fertilizer_composition_P = int(df_fertilizer_products.loc[fertilizer_product, "P"])
    fertilizer_composition_K = int(df_fertilizer_products.loc[fertilizer_product, "K"])
    return (
        fertilizer_composition_N,
        fertilizer_composition_P,
        fertilizer_composition_K,
    )


(
    fertilizer_composition_N,
    fertilizer_composition_P,
    fertilizer_composition_K,
) = select_fertilizer(fertilizer_product)


# PRODUCT Requirements by element - in Kilograms
def calculate_product_requirements(
    surface, surface_unit, field_requirement_N, field_requirement_P, field_requirement_K
):
    """Calculates Element requirements as Kilograms of N, P and K

    Args:
        surface (_type_): _description_
        surface_unit (_type_): _description_

    Returns:
        (int, int, int): required elements (in kilos) to fertilize all the surface, based on field needs
    """

    if surface_unit == "m2 - sqm":
        surface = surface / 10000
    if surface_unit == "acres":
        surface = surface * 0.4046856422
    element_requirement_N = field_requirement_N * surface
    element_requirement_P = field_requirement_P * surface
    element_requirement_K = field_requirement_K * surface

    return element_requirement_N, element_requirement_P, element_requirement_K


element_requirement_N, element_requirement_P, element_requirement_K = (
    calculate_product_requirements(
        surface,
        surface_unit,
        field_requirement_N,
        field_requirement_P,
        field_requirement_K,
    )
)

# Fertilizer Product Requirement in weight
product_requirement_N = 0
product_requirement_P = 0
product_requirement_K = 0

# For application display and haddle division by 0
show_results = False
impossible_N = False
impossible_P = False
impossible_K = False


###########################################################
###                State Functions                      ###
###########################################################


def calculate_requirements(state):
    (
        state.element_requirement_N,
        state.element_requirement_P,
        state.element_requirement_K,
    ) = calculate_product_requirements(
        state.surface,
        state.surface_unit,
        state.field_requirement_N,
        state.field_requirement_P,
        state.field_requirement_K,
    )

    # N
    if state.element_requirement_N == 0 and state.fertilizer_composition_N == 0:
        state.product_requirement_N = 0
        state.impossible_N = False
    elif state.fertilizer_composition_N == 0:
        state.impossible_N = True
    else:
        state.product_requirement_N = state.element_requirement_N / (
            fertilizer_composition_N / 100
        )
        state.impossible_N = False

    # P
    if state.element_requirement_P == 0 and state.fertilizer_composition_P == 0:
        state.product_requirement_P = 0
        state.impossible_P = False
    elif state.fertilizer_composition_P == 0:
        state.impossible_P = True
    else:
        state.product_requirement_P = state.element_requirement_P / (
            fertilizer_composition_P / 100
        )
        state.impossible_P = False

    # K
    if state.element_requirement_K == 0 and state.fertilizer_composition_K == 0:

        state.product_requirement_K = 0
        state.impossible_K = False
    elif state.fertilizer_composition_K == 0:
        state.impossible_K = True
    else:
        state.product_requirement_K = state.element_requirement_K / (
            state.fertilizer_composition_K / 100
        )
        state.impossible_K = False

    state.show_results = True


def on_change_product(state):
    (
        state.fertilizer_composition_N,
        state.fertilizer_composition_P,
        state.fertilizer_composition_K,
    ) = select_fertilizer(state.fertilizer_product)


###########################################################
###                      Design Page                    ###
###########################################################


with tgb.Page() as fertilizing_app_page:
    tgb.text("# Taipy Fertilizing App", mode="md")

    with tgb.layout("1 1"):
        with tgb.part():
            tgb.text("## Size of Your Field", mode="md")
            with tgb.layout("1 1 1"):
                tgb.number("{surface}")
                tgb.selector(
                    value="{surface_unit}", lov="{surface_choices}", dropdown=True
                )

            tgb.text("## Requirements for Your Field", mode="md")
            tgb.text("**Requirements in Kg / ha**", mode="md")

            with tgb.layout("1 1 1"):
                tgb.number("{field_requirement_N}", label="Required N dose")
                tgb.number("{field_requirement_P}", label="Required P dose")
                tgb.number("{field_requirement_K}", label="Required K dose")

            tgb.text("## Composition of Your Fertilizer", mode="md")
            tgb.selector(
                value="{fertilizer_product}",
                lov="{fertilizer_list}",
                dropdown=True,
                on_change=on_change_product,
            )
            with tgb.layout("1 1 1"):
                tgb.number("{fertilizer_composition_N}", label="N composition")
                tgb.number("{fertilizer_composition_P}", label="P composition")
                tgb.number("{fertilizer_composition_K}", label="K composition")

            tgb.button(label="calculate", on_action=calculate_requirements)

        with tgb.part(render="{show_results}"):
            tgb.text("## Fertilizer Needs for {surface} {surface_unit}", mode="md")
            tgb.text("* Ideally {round(element_requirement_N, 2)} Kg of N", mode="md")
            tgb.text("* Ideally {round(element_requirement_P, 2)} Kg of P", mode="md")
            tgb.text("* Ideally {round(element_requirement_K, 2)} Kg of K", mode="md")

            tgb.text("### Required {fertilizer_product}", mode="md")

            with tgb.part(render="{impossible_N}"):
                tgb.text(
                    "Your fertilizer doesn't have any N, you can't satisfy your needs"
                )
            with tgb.part(render="{impossible_N == False}"):
                tgb.text(
                    "* You need {round(product_requirement_N, 2)} Kg of {fertilizer_product} to satisfy your N requirements",
                    mode="md",
                )
            with tgb.part(render="{impossible_P}"):
                tgb.text(
                    "Your fertilizer doesn't have any P, you can't satisfy your needs"
                )
            with tgb.part(render="{impossible_P == False}"):
                tgb.text(
                    "* You need {round(product_requirement_P, 2)} Kg of {fertilizer_product} to satisfy your P requirements",
                    mode="md",
                )
            with tgb.part(render="{impossible_K}"):
                tgb.text(
                    "Your fertilizer doesn't have any K, you can't satisfy your needs"
                )
            with tgb.part(render="{impossible_K == False}"):
                tgb.text(
                    "* You need {round(product_requirement_K, 2)} Kg of {fertilizer_product} to satisfy your K requirements",
                    mode="md",
                )

###########################################################
###                       Run App                       ###
###########################################################

gui = Gui(fertilizing_app_page)


if __name__ == "__main__":
    gui.run(
        use_reloader=True,
        title="Fertilizer calculator",
        port=2452,
        dark_mode=False,
    )
