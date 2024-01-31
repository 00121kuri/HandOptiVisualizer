from enum import Enum

class ScoreType(Enum):
    SCORE = (1, 'score', 'score', r'$L_{\text{total}}$', 'blue')
    DISTANCE = (2, 'distance', 'distanceScore', r'$L_{\text{position}}$', 'orange')
    ROTATION = (3, 'rotationScore', 'rotationScore', r'$L_{\text{rotation}}$', 'green')
    INIT_CHROMOSOME = (4, 'initChromosomeDiffScore', 'initChromosomeDiffScore', r'$L_{\text{previous}}$', 'red')
    INPUT_CHROMOSOME = (5, 'inputChromosomeDiffScore', 'inputChromosomeDiffScore', r'$L_{\text{input}}$', 'purple')
    ANGLE_DIFF = (6, 'angleDiff', 'angleDiff', 'Angle Difference [deg]', 'brown')

    def __init__(self, id, name_db, name_csv, label, color) -> None:
        super().__init__()
        self.id = id
        self.name_db = name_db
        self.name_csv = name_csv
        self.label = label
        self.color = color

    @property
    def name_db_list(self):
        return [score_type.name_db for score_type in ScoreType]
    
    @property
    def name_csv_list(self):
        return [score_type.name_csv for score_type in ScoreType]
    