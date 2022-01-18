from . import rsmain, rssampling, rssim, rsuse
from .picker import Picker


class Writer:
    def __init__(self):
        self.use = rsuse.APHRECO_PRELUDE
        self.main = ""
        # simulation
        self.struct = ""
        self.simtrait = ""
        self.smp_t = ""
        # optimization
        self.opttrait = ""
        self.data = ""

    def write(self, source: Picker):
        #  set self.main
        self._write_sim_main()

        # set self.struct
        self._write_struct()

        # set self.simtrait
        self._write_sim_model(source)

        # set self.sampling_time
        self._write_sampling_time(source)

        rust_code = ""
        rust_code += self.use
        rust_code += self.main
        rust_code += self.struct
        rust_code += self.simtrait
        rust_code += self.smp_t

        return rust_code

    def write_sim(self):
        pass

    def write_opt(self):
        pass

    def _write_sim_main(self):
        main_header = rsmain.HEADER
        main_body = rsmain.SIM_BODY
        main_footer = rsmain.FOOTER
        self.main = main_header + main_body + main_footer

    def _write_struct(self):
        model_const = rssim.CONST
        struct = rssim.STRUCT
        self.struct = model_const + struct

    def _write_sim_model(self, picker: Picker):
        # connect all
        model_code = rssim.IMPL_SIMTRAIT
        model_code += rssim.write_fn_new(picker.p)
        model_code += rssim.write_fn_init(picker.t, picker.y)
        model_code += rssim.write_fn_ode(picker.ode)
        model_code += rssim.write_fn_rec(picker.rec)
        model_code += rssim.write_fn_cond(picker.cond)
        model_code += rssim.write_fn_beat(picker.beat)
        model_code += rssim.write_fn_cre(picker.cre)
        model_code = model_code[:-1] + "}\n\n"  # end impl
        self.simtrait = model_code

    def _write_sampling_time(self, picker: Picker):
        self.smp_t = rssampling.write_fn_sampling_time("")

    def save(self, path):
        pass
