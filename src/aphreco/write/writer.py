from . import rsmain, sim


class Writer:
    def __init__(self):
        pass

    def rs_main(self):
        main_header = rsmain.MAIN_HEADER
        main_body = rsmain.MAIN_BODY
        main_footer = rsmain.MAIN_FOOTER
        return main_header + main_body + main_footer

    def rs_sim_model(self, ode_code: str, rec_code: str):
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
        model_code += ode_code
        model_code += rec_code
        model_code = model_code[:-1] + "}\n"  # end impl

        return model_code

    def rs_ode(self, str_ode: str):
        header = sim.ODE_HEADER

        indent = " " * 4
        body = ""
        for line in str_ode.splitlines():
            body += indent + line + ";\n"

        footer = sim.ODE_FOOTER
        return header + body + footer

    def rs_rec(self, str_rec: str):
        header = sim.REC_HEADER

        act_indent = " " * 4
        delta_indent = " " * 6
        body = ""
        beat_id = 0
        for line in str_rec.splitlines():
            if line.startswith("==="):
                if beat_id > 0:
                    body += act_indent + "}\n"
                body += act_indent + "if act[" + str(beat_id) + "] {\n"
            else:
                body += delta_indent + line + ";\n"
        body += act_indent + "}\n"

        footer = sim.REC_FOOTER
        return header + body + footer
