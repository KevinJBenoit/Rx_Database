

class Rx():
    def __init__(self, rank, drug_name, total_rx):
        self.rank = rank
        self.drug_name = drug_name
        self.total_rx = total_rx
    def __repr__(self):
            return "rank = {}, drug_name = {}, total_rx = {}".format(self.rank, self.drug_name, self.total_rx)