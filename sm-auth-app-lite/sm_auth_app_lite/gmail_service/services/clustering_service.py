import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from typing import List, Dict
from ..constants import DBSCAN_EPS, DBSCAN_MIN_SAMPLES, CATEGORY_MAPPING

class ClusteringService:
    def process_embeddings(self, emails_df: pd.DataFrame) -> pd.DataFrame:
        """
        Process all email embeddings at once using DBSCAN
        
        Args:
            emails_df: DataFrame with 'embedding' column containing email embeddings
            
        Returns:
            DataFrame with added 'category' column
        """
        # Stack embeddings into 2D array for DBSCAN
        embeddings_array = np.stack(emails_df['embedding'].values)
        
        # Perform clustering
        clustering = DBSCAN(
            eps=DBSCAN_EPS,
            min_samples=DBSCAN_MIN_SAMPLES
        ).fit(embeddings_array)
        
        # Map cluster labels to categories
        emails_df['category'] = [CATEGORY_MAPPING.get(label, 'D') 
                               for label in clustering.labels_]
        
        return emails_df 