# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import numpy as np
from ReadBulletScreen import BulletScreen
import ldaModel
import uniout
import copy
import os

try:
    import cPickle as pickle
except ImportError:
    import pickle


def grab_C_list():
        fr = open("data/var/C_list_tfidf", "rb")
        C_list = pickle.load(fr)
        #print C_list[0].shape
        fr.close()
        return C_list

def grab_T_list():
        fr = open("data/var/T_list", "rb")
        T_list = pickle.load(fr)
        fr.close()
        return T_list

def grab_lineno_list():
    fr = open("data/var/lineno_list", "rb")
    lineno_list = pickle.load(fr)
    fr.close()
    return lineno_list

def grab_slice_number():
    fr = open("data/var/slice_number", "rb")
    slice_number = pickle.load(fr)
    fr.close()
    return slice_number




def distance(M,N):
    return np.linalg.norm(M - N)

class SJTTR(object):

    def __init__(self,rho=0.5,gamma=0.8,l_ambda=200,m=5,w=4):
        self.C_list=grab_C_list()

        #print self.C_list[0].shape
        self.T_list=grab_T_list()
        self.lineno_list=grab_lineno_list()
        self.slice_number=grab_slice_number()
        self.rho=rho
        self.gamma=gamma
        self.Lambda=l_ambda
        self.K=len(self.T_list)
        self.m=m
        self.w=w
        self.X_list=[]

        self.selected_C_i=[]
        self.selected_T_i=[]



    def initialize_A_B_beta(self,N_old,N_new):
        old_A_k=np.full((N_old,N_new),10)
        old_B_k=np.full((N_old,N_new),10)
        old_beta_k=np.zeros(N_new)
        return old_A_k,old_B_k,old_beta_k


    def _beta_k(self,old_A_k,old_B_k,theta_k):
        return np.sqrt(self.rho*np.sum(old_A_k**2,axis=0)+(1-self.rho)*np.sum(old_B_k**2,axis=0) /(self.Lambda*theta_k))


    def _A_k(self,k,new_beta_k,old_A_k):
        if k==0:

            numberator=np.dot(self.C_list[k].T,self.C_list[k])
            denumberator=np.dot(old_A_k,numberator)+np.dot(old_A_k,np.linalg.inv(np.diag(new_beta_k)))
            #if any elements of denumberator is 0 ,the result there should be set 0
            _denumberator=np.where(denumberator==0,-1,denumberator)
            result=numberator/_denumberator*old_A_k
            return np.where(result<0,0,result)
        else:
            numberator = np.dot(self.C_list[k].T,self.C_hat)


            _temp=1/np.where(new_beta_k == 0, -1, new_beta_k)
            print self.C_hat.shape
            denumberator = np.dot(np.dot(old_A_k, self.C_hat.T) ,self.C_hat)+ np.dot(old_A_k, \
                                                                                     np.diag(np.where(_temp < 0, 0, _temp)))
            # if any elements of denumberator is 0 ,the result there should be set 0
            _denumberator = np.where(denumberator == 0, -1,denumberator)
            result = numberator / _denumberator * old_A_k
            return np.where(result < 0, 0, result)


    def _B_k(self,k,new_beta_k,old_B_k):
        if k == 0:
            numberator = np.dot(self.T_list[k].T,self.T_list[k])
            denumberator =np.dot(old_B_k,numberator) + np.dot(old_B_k, np.linalg.inv(np.diag(new_beta_k)))
            _denumberator = np.where(denumberator == 0, -1, denumberator)
            result=numberator/_denumberator*old_B_k
            return np.where(result<0,0,result)
        else:
            numberator = np.dot(self.T_list[k].T,self.T_hat)
            _temp = 1 / np.where(new_beta_k == 0, -1, new_beta_k)
            denumberator= np.dot(np.dot(old_B_k, self.T_hat.T),self.T_hat)+np.dot(old_B_k,np.diag(np.where(_temp < 0, 0, _temp)))
            _denumberator= np.where(denumberator == 0, -1, denumberator)
            result = numberator / _denumberator * old_B_k
            return np.where(result<0,0,result)



    def display_comment(self):

        print self.X_list
        with open("data/representative.txt", 'w') as f:
            with open("../Datasets/scripts/final.json", 'r') as f2:
                lines = json.load(f2)
                for i,item in enumerate(self.X_list):
                    f.write("time slice:"+str(i)+"\n")
                    for item2 in item:
                        # f.write(lines[int(item2)-1]+"\n")
                        st = "<d p=\"" + str(lines[int(item2)]["time"]) + "\">" + str(lines[int(item2)]["message"]) + "</d>\n"
                        f.write(st)
                    f.write("\n")


    def estimation(self):
        index=0
        for k in xrange(self.K):
            if k==0:
                N_old=self.C_list[k].shape[1]
                self.temp_N_old=N_old
                self.old_A_k,self.old_B_k,self.old_beta_k=self.initialize_A_B_beta(N_old,N_old)
                self.theta_k =np.full(N_old,1.0,dtype=float)
                while True:
                    self.new_beta_k=self._beta_k(self.old_A_k,self.old_B_k,np.full(N_old,1.0,dtype=float))
                    print "%d beta_k: %d" % (k,index)

                    # print self.new_beta_k
                    # print len(self.new_beta_k)
                    while True:
                        self.new_A_k=self._A_k(k,self.new_beta_k,self.old_A_k)
                        dis=distance(self.old_A_k,self.new_A_k)
                        print "%d A dis: %f" % (k,dis)
                        if dis<=0.01:
                            break
                        else:
                            self.old_A_k=self.new_A_k
                        index+=1
                        print " %d A loop: %d" % (k,index)

                    while True:
                        self.new_B_k = self._B_k(k, self.new_beta_k, self.old_B_k)
                        dis=distance(self.old_B_k, self.new_B_k)
                        print "%d B dis: %f" % (k, dis)
                        if  dis<= 0.01:
                            break
                        else:
                            self.old_B_k = self.new_B_k
                        index+=1
                        print "%d B loop: %d" % (k,index)
                    dis=distance(self.old_beta_k,self.new_beta_k)
                    print "%d beta dis: %f" % (k, dis)
                    if dis<=0.01:
                        break
                    else:
                        self.old_beta_k=self.new_beta_k
                        index+=1
                        print " %d beta loop: %d" % (k, index)
            else:
                print self.C_hat.shape
                print self.T_hat.shape


                N_old = self.C_list[k].shape[1]
                self.temp_N_old = N_old
                print
                if  k<self.w:
                    N_new=N_old+self.m*k
                else:
                    N_new=N_old+self.m*self.w

                self.old_A_k, self.old_B_k, self.old_beta_k =self.initialize_A_B_beta(N_old,N_new)

                print "%d beta_k: %d" % (k, index)

                while True:
                    self.new_beta_k = self._beta_k(self.old_A_k, self.old_B_k,self.theta_k)
                    print "%d beta_k: %d" % (k, index)
                    # print self.new_beta_k
                    while True:
                        self.new_A_k = self._A_k(k, self.new_beta_k, self.old_A_k)
                        dis=distance(self.old_A_k, self.new_A_k)
                        print "%d A dis: %f" % (k, dis)
                        if dis <= 0.01:
                            break
                        else:
                            self.old_A_k = self.new_A_k
                        index += 1
                        print " %d A loop: %d" % (k, index)

                    while True:
                        self.new_B_k = self._B_k(k, self.new_beta_k, self.old_B_k)
                        dis=distance(self.old_B_k, self.new_B_k)
                        print "%d B dis: %f" % (k, dis)
                        if dis <= 0.01:
                            break
                        else:
                            self.old_B_k = self.new_B_k
                        index += 1
                        print " %d B loop: %d" % (k, index)
                    dis=distance(self.old_beta_k, self.new_beta_k)
                    print "%d beta dis: %f" % (k, dis)
                    if  dis<= 0.01:
                        break
                    else:
                        self.old_beta_k=self.new_beta_k
                        index += 1
                        print " %d beta loop: %d" % (k, index)

            if k == 0:
                self.C_hat, self.T_hat,self.theta_k = self._augumented_C_and_T(k+1, self.C_list[0], self.T_list[0])

            elif k<self.K-1:
                self.C_hat, self.T_hat,self.theta_k = self._augumented_C_and_T(k+1, self.C_hat, self.T_hat)

            else:
                self._calc_last_comment(k)

        self.display_comment()


        # augugment C_hat and T_hat
    def _augumented_C_and_T(self, k, old_C_hat, old_T_hat):
        # corresponding to the index of beta

        rp_comment = [item[1] for item in sorted([(item, i) for i, item in enumerate(self.new_beta_k[:self.temp_N_old])], \
                                                 key=lambda x: x[0], reverse=True)[:self.m]]



        # print rp_comment
        # print k
        # print self.lineno_list[k - 1]
        # corresponding to the index of lineno
        self.X_list.append([self.lineno_list[k - 1][item] for item in rp_comment])



        C_hat = [item for item in self.C_list[k].T]
        T_hat = [item for item in self.T_list[k].T]

        #initialize theta
        theta_k=[1.0 for item in self.C_list[k].T]

        self.selected_C_i.append([old_C_hat.T[item] for item in rp_comment])
        self.selected_T_i.append([old_T_hat.T[item] for item in rp_comment])

        # if k==1:
        #     for item in rp_comment:
        #         C_hat.append(old_C_hat.T[item])
        #         T_hat.append(old_T_hat.T[item])
        if k<self.w:
            for index in xrange(len(self.selected_C_i)):
                for item in self.selected_C_i[index]:
                    C_hat.append(item)
                    theta_k.append(np.exp(float(k - index - self.w) / self.gamma))
                for item in self.selected_T_i[index]:
                    T_hat.append(item)
        else:
            for index in range(k-self.w,k):
                for item in self.selected_C_i[index]:
                    C_hat.append(item)
                    theta_k.append(np.exp(float(k - index - self.w) / self.gamma))
                for item in self.selected_T_i[index]:
                    T_hat.append(item)

        return np.array(C_hat).T, np.array(T_hat).T,np.array(theta_k)


    def _calc_last_comment(self,k):
        rp_comment = [item[1] for item in sorted([(item, i) for i, item in enumerate(self.new_beta_k[:self.temp_N_old])], \
                                                 key=lambda x: x[0], reverse=True)[:self.m]]
        self.X_list.append([self.lineno_list[k][item] for item in rp_comment])



if __name__=="__main__":
    SJTTR().estimation()
