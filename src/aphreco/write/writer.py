from . import rsmain, sim


class Writer:
    def __init__(self):
        pass

    def rs_main(self):
        main_header = rsmain.MAIN_HEADER
        main_body = rsmain.MAIN_BODY
        main_footer = rsmain.MAIN_FOOTER
        return main_header + main_body + main_footer

    def rs_sim_model(self, ode: str):
        const = sim.CONST
        struct = sim.STRUCT
        new_header = sim.NEW_HEADER
        new_body = sim.NEW_BODY
        new_footer = sim.NEW_FOOTER
        # connect all
        model_code = ""
        model_code += const
        model_code += struct
        model_code += new_header + new_body + new_footer
        return model_code

    def rs_ode(self, str_ode: str):
        header = sim.ODE_HEADER

        indent = " " * 4
        body = ""
        for line in str_ode.splitlines():
            body += indent + line + ";\n"
        body = body

        footer = sim.ODE_FOOTER
        return header + body + footer
