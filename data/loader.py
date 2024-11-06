from pymongo import MongoClient
import pandas as pd
from pandas import DataFrame
from torch_geometric.transforms import RandomLinkSplit
from torch_geometric.loader import LinkNeighborLoader

class MongoLoader:
  def __init__(self,uri:str,db_name:str) -> None:
    self.mongo_client = MongoClient(uri)
    self.db = self.mongo_client[db_name]

  def to_df(self,owner:str,name:str,collection_name:str,filter) -> DataFrame:
      query = {"owner": owner, "name": name}
      contents = list(self.db[collection_name].find(query))
      contents_df = pd.DataFrame(contents)
      contents_df = contents_df[filter]
      return contents_df
  


# 将数据划分为训练集、验证集和测试集
# 使用 RandomLinkSplit 划分 'resolve' 边
def split_dataset(data):
    print("将数据划分为训练集、验证集------------------------------------------")
    dataset_split = RandomLinkSplit(
        num_val=0.1,
        num_test=0, # 测试集单独提供
        is_undirected=True,
        add_negative_train_samples=True,
        edge_types=[('issue', 'resolved_by', 'user')],
        rev_edge_types=[('user', 'rev_resolved_by', 'issue')]
    )
    train_data, val_data, _ = dataset_split(data)
    return train_data, val_data

def dataset_to_batch(train_data,val_data,batch_size):
      # 创建数据加载器
    num_neighbors=[10, 10] # 每层采样的邻居数，可以根据需要调整
    print("train_loader ---------------------------------")
    train_loader = LinkNeighborLoader(
        train_data,
        num_neighbors=num_neighbors, 
        edge_label_index=(('issue', 'resolved_by', 'user'),
        train_data['issue', 'resolved_by', 'user'].edge_label_index
        ),
        edge_label=train_data['issue', 'resolved_by', 'user'].edge_label,
        batch_size=batch_size,
        shuffle=True
    )
    print("val_loader ---------------------------------")
    val_loader = LinkNeighborLoader(
        val_data,
        num_neighbors=num_neighbors,
        edge_label_index=(('issue', 'resolved_by', 'user'),
        val_data['issue', 'resolved_by', 'user'].edge_label_index
        ),
        edge_label=val_data['issue', 'resolved_by', 'user'].edge_label,
        batch_size=batch_size,
        shuffle=False
    )
    # print("test_loader ---------------------------------")
    # self.test_loader = LinkNeighborLoader(
    # self.test_data,
    # num_neighbors=num_neighbors,
    # edge_label_index=(('issue', 'resolved_by', 'user'),
    # self.test_data['issue', 'resolved_by', 'user'].edge_label_index
    # ),
    # edge_label=self.test_data['issue', 'resolved_by', 'user'].edge_label,
    # batch_size=batch_size,
    # shuffle=False
    # ) 
    return train_loader,val_loader
  




