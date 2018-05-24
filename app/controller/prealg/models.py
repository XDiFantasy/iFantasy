from mxnet import nd
from mxnet.gluon import nn, rnn
import mxnet as mx


class SampleMLP(nn.Block):
    def __init__(self, bn=False, dropout=None,**kwargs):
        super(SampleMLP,self).__init__(**kwargs)
        self.bn = bn
        self.dropout = dropout
        with self.name_scope():
            self.conv = nn.Conv1D(channels=5,kernel_size=3)
            self.flatten = nn.Flatten()
            self.dense0 = nn.Dense(128,activation='tanh')
            self.dense1 = nn.Dense(64,activation='tanh')
            self.dense2 = nn.Dense(32,activation='tanh')
            self.output = nn.Dense(1)
    def forward(self,x):
        x = self.flatten(self.conv(x.reshape(shape=(-1,5,11))))
        return self.output(self.dense2(self.dense1(self.dense0(x))))

class MLP4(nn.Block):
    def __init__(self, net,bn=False, dropout=None,**kwargs):
        super(MLP4,self).__init__(**kwargs)
        self.bn = bn
        self.dropout = dropout
        self.net = net
        self.build()
        


    def build(self):
        with self.name_scope():
            self.conv = nn.Conv1D(channels=5,kernel_size=3)
            #self.mp = nn.MaxPool1D(pool_size=2)
            self.flatten = nn.Flatten()
            self.dense0 = nn.Dense(self.net[0][0],activation=self.net[0][1])
            self.dense1 = nn.Dense(self.net[1][0],activation=self.net[1][1])
            self.dense2 = nn.Dense(self.net[2][0],activation=self.net[2][1])
            self.dense3 = nn.Dense(self.net[3][0],activation=self.net[3][1])
            if self.bn:
                print(self.bn)
                self.bn0 = nn.BatchNorm(axis=1)
                self.bn1 = nn.BatchNorm(axis=1)
                self.bn2 = nn.BatchNorm(axis=1)
                self.bn3 = nn.BatchNorm(axis=1)
            if self.dropout is not None:
                self.dropout0 = nn.Dropout(self.dropout[0])
                self.dropout1 = nn.Dropout(self.dropout[1])
                self.dropout2 = nn.Dropout(self.dropout[2])
                self.dropout3 = nn.Dropout(self.dropout[3])
            self.output = nn.Dense(1)
    def forward(self, data):
        #data input shape : n*55
        #data this shape : n*5*11
        data = self.flatten(self.conv(data.reshape(shape=(-1,5,11))))
        if self.bn and not self.dropout:
            return self.output(self.bn3(self.dense3(self.bn2(self.dense2(self.bn1(self.dense1(self.bn0(self.dense0(data)))))))))
        elif not self.bn and self.dropout:
            return self.output(self.dropout3(self.dense3(self.dropout2(self.dense2(self.dropout1(self.dense1(self.dropout0(self.dense0(data)))))))))
        elif not self.bn and not self.dropout:
            return self.output(self.dense3(self.dense2(self.dense1(self.dense0(data)))))
        return self.output(self.dropout3(self.bn3(self.dense3(self.dropout2(self.bn2(self.dense2(self.dropout1(self.bn1(self.dense1(self.dropout0(self.bn0(self.dense0(data)))))))))))))
class MLP3(nn.Block):
    def __init__(self, bn=False, dropout=None,**kwargs):
        super(MLP3,self).__init__(**kwargs)
        self.bn = bn
        self.dropout = dropout
        self.build()


    def build(self):
        with self.name_scope():
            self.conv = nn.Conv1D(channels=5,kernel_size=3)
            #self.mp = nn.MaxPool1D(pool_size=2)
            self.flatten = nn.Flatten()
            self.dense0 = nn.Dense(128,activation='sigmoid')
            self.dense1 = nn.Dense(128,activation='sigmoid')
            self.dense2 = nn.Dense(128,activation='sigmoid')
            #self.dense3 = nn.Dense(16,activation='tanh')
            if self.bn:
                print(self.bn)
                self.bn0 = nn.BatchNorm(axis=1)
                self.bn1 = nn.BatchNorm(axis=1)
                self.bn2 = nn.BatchNorm(axis=1)
                self.bn3 = nn.BatchNorm(axis=1)
            if self.dropout is not None:
                self.dropout0 = nn.Dropout(self.dropout[0])
                self.dropout1 = nn.Dropout(self.dropout[1])
                self.dropout2 = nn.Dropout(self.dropout[2])
                self.dropout3 = nn.Dropout(self.dropout[3])
            self.output = nn.Dense(1)
    def forward(self, data):
        #data input shape : n*55
        #data this shape : n*5*11
        data = self.flatten(self.conv(data.reshape(shape=(-1,5,11))))
        if self.bn and not self.dropout:
            return self.output(self.bn3(self.bn2(self.dense2(self.bn1(self.dense1(self.bn0(self.dense0(data))))))))
        elif not self.bn and self.dropout:
            return self.output(self.dropout3(self.dropout2(self.dense2(self.dropout1(self.dense1(self.dropout0(self.dense0(data))))))))
        elif not self.bn and not self.dropout:
            return self.output(self.dense2(self.dense1(self.dense0(data))))
        return self.output(self.dropout3(self.bn3(self.dropout2(self.bn2(self.dense2(self.dropout1(self.bn1(self.dense1(self.dropout0(self.bn0(self.dense0(data))))))))))))
class MLP2(nn.Block):
    def __init__(self, net,bn=False, dropout=None,**kwargs):
        super(MLP2,self).__init__(**kwargs)
        self.bn = bn
        self.dropout = dropout
        self.build()
        self.net = net


    def build(self):
        with self.name_scope():
            self.conv = nn.Conv1D(channels=5,kernel_size=3)
            #self.mp = nn.MaxPool1D(pool_size=2)
            self.flatten = nn.Flatten()
            self.dense0 = nn.Dense(self.net[0][0],activation=self.net[0][1])
            self.dense1 = nn.Dense(self.net[1][0],activation=self.net[1][1])
            #self.dense2 = nn.Dense(32,activation='tanh')
            #self.dense3 = nn.Dense(16,activation='tanh')
            if self.bn:
                print(self.bn)
                self.bn0 = nn.BatchNorm(axis=1)
                self.bn1 = nn.BatchNorm(axis=1)
                self.bn2 = nn.BatchNorm(axis=1)
                self.bn3 = nn.BatchNorm(axis=1)
            if self.dropout is not None:
                self.dropout0 = nn.Dropout(self.dropout[0])
                self.dropout1 = nn.Dropout(self.dropout[1])
                self.dropout2 = nn.Dropout(self.dropout[2])
                self.dropout3 = nn.Dropout(self.dropout[3])
            self.output = nn.Dense(1)
    def forward(self, data):
        #data input shape : n*55
        #data this shape : n*5*11
        data = self.flatten(self.conv(data.reshape(shape=(-1,5,11))))
        if self.bn and not self.dropout:
            return self.output(self.bn3(self.bn2(self.bn1(self.dense1(self.bn0(self.dense0(data)))))))
        elif not self.bn and self.dropout:
            return self.output(self.dropout3(self.dropout2(self.dropout1(self.dense1(self.dropout0(self.dense0(data)))))))
        elif not self.bn and not self.dropout:
            return self.output(self.dense1(self.dense0(data)))
        return self.output(self.dropout3(self.bn3(self.dropout2(self.bn2(self.dropout1(self.bn1(self.dense1(self.dropout0(self.bn0(self.dense0(data)))))))))))



class CMLP(MLP4):
    def __init__(self,output_dim,bn=False,dropout=None,**kwargs):
        self.output_dim = output_dim
        super(CMLP,self).__init__(bn=bn,dropout=dropout,**kwargs)
        
    def build(self):
        with self.name_scope():
            self.dense0 = nn.Dense(512,activation='relu')
            self.dense1 = nn.Dense(256, activation='relu')
            self.dense2 = nn.Dense(128, activation='relu')
            self.dense3 = nn.Dense(64, activation='relu')
            #self.dense2 = nn.Dense(32, activation='relu')
            self.output = nn.Dense(self.output_dim)
    def forward(self, x):
        a1 = self.dense0(x)
        a2 = self.dense1(a1)
        a3 = self.dense2(a2)
        a4 = self.dense3(a3)
        o = self.output(a4)
        
        return o

class RNN(nn.Block):
    def __init__(self, mode, embed_dim, hidden_dim,
                 num_layers, dropout=0.5, **kwargs):
        super(RNN, self).__init__(**kwargs)
        with self.name_scope():
            self.drop = nn.Dropout(dropout)
            # self.encoder = nn.Embedding(vocab_size, embed_dim,
            #                             weight_initializer=mx.init.Uniform(0.1))
            if mode == 'rnn_relu':
                self.rnn = rnn.RNN(hidden_dim, num_layers, activation='relu',
                                   dropout=dropout, input_size=embed_dim)
            elif mode == 'rnn_tanh':
                self.rnn = rnn.RNN(hidden_dim, num_layers, activation='tanh',
                                   dropout=dropout, input_size=embed_dim)
            elif mode == 'lstm':
                self.rnn = rnn.LSTM(hidden_dim, num_layers, dropout=dropout,
                                    input_size=embed_dim)
            elif mode == 'gru':
                self.rnn = rnn.GRU(hidden_dim, num_layers, dropout=dropout,
                                   input_size=embed_dim)
            else:
                raise ValueError("Invalid mode %s. Options are rnn_relu, "
                                 "rnn_tanh, lstm, and gru"%mode)

            self.decoder = nn.Dense(1, in_units=hidden_dim)
            self.hidden_dim = hidden_dim

    def forward(self, inputs, state):
        #emb = self.drop(self.encoder(inputs))
        
        output, state = self.rnn(inputs, state)
        #output = self.drop(output)
        
        decoded = self.decoder(output.reshape((-1, self.hidden_dim)))
        #print("inforward",decoded.shape)
        return decoded, state

    def begin_state(self, *args, **kwargs):
        return self.rnn.begin_state(*args, **kwargs)

def detach(state):
    if isinstance(state, (tuple, list)):
        state = [i.detach() for i in state]
    else:
        state = state.detach()
    return state
def evals(net, adata ,alabel, batch_size):
    hidden = net.begin_state(func=mx.nd.zeros,batch_size = batch_size,ctx=mx.cpu())
    dataLoader = DataLoader(adata, alabel)
    tl = 0
    for data, label in dataLoader.dataIter(batch_size):
        label = nd.array(label)
        #label = nd.ones(shape=(5,batch_size)) * label
        #label = label.reshape((-1,))
        dd = nd.array(data.reshape((batch_size,5,11)).swapaxes(0,1))
        #hidden = detach(hidden)
        output,hidden = net(dd, hidden)
        output = output.reshape((5,batch_size,1))
        output = nd.sum(output,axis=0)/5
        lv = loss(output, label)

        tl += nd.sum(lv).asscalar()
    return tl / len(adata)
def predict(net, data, label):
    data = nd.array(data)
    label = nd.array(label)
    hidden = net.begin_state(func=mx.nd.zeros,batch_size = data.shape[0],ctx=mx.cpu())
    dd = nd.array(data.reshape((data.shape[0],5,11)).swapaxes(0,1))
    output,hidden = net(dd,hidden)
    output = output.reshape((5,data.shape[0],1))
    output = nd.sum(output,axis=0)/5
    l = nd.argmax(output, axis=1)
    res = nd.mean(l==label)
    return res.asscalar()

if __name__ == '__main__':
    from utils import loadDataLabel3, DataLoader
    a,b,c,d = loadDataLabel3('three_pt',0.7)
    print(d.shape)
    rnn = RNN("rnn_tanh",11,100,2)
    rnn.collect_params().initialize(mx.init.Xavier())
    batch_size = 256
    clipping_norm = 0.1
    num_steps = 5
    loss = mx.gluon.loss.L2Loss()
    trainer = mx.gluon.Trainer(rnn.collect_params(),'sgd',{
        'learning_rate':0.5,
        "wd":0.00
    })
    dataLoader = DataLoader(a,b)
    trl = []
    tel = []
    for epoch in range(500):
        total_L = 0.0
        hidden = rnn.begin_state(func=mx.nd.zeros,batch_size = batch_size,ctx=mx.cpu())

        for data,label in dataLoader.dataIter(batch_size):
            label = nd.array(label)
           # print("label shape" ,label.shape)
            #label = nd.ones(shape=(5,32)) * label
            #label = label.reshape((-1,))
            dd = nd.array(data.reshape((batch_size,5,11)).swapaxes(0,1))
            hidden = detach(hidden)
            with mx.autograd.record():
                output, hidden = rnn(dd,hidden)
                output = output.reshape((5,256,1))
                output = nd.sum(output,axis=0)/5
               # print(output.shape)
                lv = loss(output,label)
            lv.backward()
            grads = [i.grad() for i in rnn.collect_params().values()]
            mx.gluon.utils.clip_global_norm(grads,clipping_norm*num_steps*batch_size)
            trainer.step(batch_size)
            total_L += mx.nd.sum(lv).asscalar()
        test_loss = evals(rnn,c,d,batch_size)
        trl.append(total_L/len(a))
        tel.append(test_loss)
        print("Epoch %d loss %.4f test loss %.4f train acc %.4f test acc %.4f" %(epoch, total_L/len(a), test_loss,predict(rnn,a,b),predict(rnn,c,d)))
    with open("rnn.csv",'w',newline='') as f:
        import csv
        writer = csv.writer(f)
        writer.writerows([trl,tel])
            
        
    
    
            
