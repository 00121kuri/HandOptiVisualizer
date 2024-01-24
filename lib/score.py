from enum import Enum

class ScoreType(Enum):
    SCORE = (1, 'score', 'score', 'Score', 'blue')
    DISTANCE = (2, 'distance', 'distanceScore', 'Distance', 'orange')
    ROTATION = (3, 'rotationScore', 'rotationScore', 'Rotation', 'green')
    INIT_CHROMOSOME = (4, 'initChromosomeDiffScore', 'initChromosomeDiffScore', 'Previous Chromosome Diff', 'red')
    INPUT_CHROMOSOME = (5, 'inputChromosomeDiffScore', 'inputChromosomeDiffScore', 'Input Chromosome Diff', 'purple')

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
    