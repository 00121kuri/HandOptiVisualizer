from enum import Enum

class ParamType(Enum):
    optiSettingHash = (1, 'optiSettingHash', 'Opti Setting Hash', 'init')
    mutationRate = (2, 'mutationRate', 'Mutation Rate', -1)
    sigma = (3, 'sigma', 'Sigma', -1)
    mean = (4, 'mean', 'Mean', 0)
    worstScore = (5, 'worstScore', 'Worst Score', -1)
    maxSteps = (6, 'maxSteps', 'Max Steps', -1)
    isUsePreviousResult = (7, 'isUsePreviousResult', 'Use Previous Result', False)
    weightDistance = (8, 'weightDistance', 'Weight Distance', 1)
    weightRotation = (9, 'weightRotation', 'Weight Rotation', 0.1)
    weightChromosomeDiff = (10, 'weightChromosomeDiff', 'Weight Previous Chromosome Diff', 0)
    weightInputChromosomeDiff = (11, 'wieghtInputChromosomeDiff', 'Weight Input Chromosome Diff', 0)
    isUseInputChromosome = (12, 'isUseInputChromosome', 'Use Input Chromosome', False)


    def __init__(self, id, param_name, label, init_val) -> None:
        super().__init__()
        self.id = id
        self.param_name = param_name
        self.label = label
        self.init_val = init_val

    @property
    def init_dict(self):
        return {param_type.param_name: param_type.init_val for param_type in ParamType}
    
    @property
    def param_name_list(self):
        return [param_type.param_name for param_type in ParamType]
    
    def param_to_init_val(param_name):
        return {param_type.param_name: param_type.init_val for param_type in ParamType if param_type.param_name == param_name}