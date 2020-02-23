import numpy as np
import pickle

from data_loader.data_objects.column import Column
from utils.utils import convert_data_type


class CorrelationClusteringColumn(Column):
    """
    A class used to represent a column of a table

    Attributes
    ----------
    data : list
        the data contained in the column
    quantiles : int
        the number of quantiles used in the histogram creation
    quantile_histogram : QuantileHistogram
        the quantile histogram representation of the column using the sorted ranks of the data

    Methods
    -------
    get_histogram()
        Returns the quantile histogram of the column

    get_original_name()
        Returns the column name

    get_original_data()
        Returns the original data instances

    get_long_name()
        Returns the compound name of the column (table_name + '_' + column_name)

    get_data_type()
        Returns the data type of the column
    """
    def __init__(self, name: str, data: list, table_name: str, dataset_name: str, quantiles: int):
        """
        Parameters
        ----------
        name : str
            The name of the column
        data : list
            The data instances of the column
        quantiles: int
            The number of quantiles of the column's quantile histogram
        """
        super().__init__(name, data, table_name)
        self.quantiles = quantiles
        self.dataset_name = dataset_name
        self.ranks = self.get_global_ranks(self.data, self.dataset_name)
        self.quantile_histogram = None

    def get_histogram(self):
        """Returns the quantile histogram of the column"""
        return self.quantile_histogram

    def get_original_data(self):
        """Returns the original data instances"""
        return self.data

    @staticmethod
    def get_global_ranks(column: list, dataset_name: str):
        with open('cache/global_ranks/' + dataset_name + '.pkl', 'rb') as pkl_file:
            global_ranks: dict = pickle.load(pkl_file)
            ranks = np.array(sorted([global_ranks[convert_data_type(x)] for x in column]))
            return ranks