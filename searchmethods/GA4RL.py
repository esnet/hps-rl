import numpy as np
import copy
import multiprocessing as mp
import simulation.rl_train_ddpg as ddpg
"""
E.g: 
    GA=GA4RL(model_name="DQN",nof_generations=3,pop_size=50,nof_elites=1,crossover_rate=0.7,mutation_prob=0.05)
    best,flog=GA.Run()
"""

class GA4RL():

    """PossibleGenesDict:
    All possible gene combinations
     for the given RL models"""
    PossibleGenesDict={
    "gamma": np.arange(1e-3, 1e-1, 1e-2),
    "learning_rate" : np.arange(1e-3, 1e-1, 1e-2),
    "hidden_layers" : np.array([2]),
    "nodes_per_layer" : np.arange(3, 256, 2),
    "batch_size" : np.array([64, 128, 500]),
    "step_size" : np.arange(1, 5, 0.5),
    "actor_learning_rate" : np.arange(1e-4, 1e-1, 1e-2),
    "critic_learning_rate" : np.arange(1e-4, 1e-1, 1e-2),
    "alpha_reward" : np.array([10, 20, 50, 100, 1000]),
    "beta_reward" : np.array([0.1, 1, 2.5, 5]),
    "gamma_reward" : np.array([0.1, 0.5, 1, 1.5, 2]),
    "epsilon" : np.arange(1e-3, 1e-1, 1e-2),
    "trajectory_size" : np.array([10, 20, 50, 100, 1000]),
    "max_kl" : np.array([0.001, 0.01, 0.1]),
    "test_iteration" : np.array([1000, 5000, 10000, 20000])
    }

    population = []
    next_population = []
    fitness_log=[]
    best_chrm=[]

    def __init__(self,model_name, action_type,env,test_env, device,opt_func, nof_generations,pop_size,nof_elites,crossover_rate,mutation_prob):
        self.model_name = model_name #RL model name, e.g DQN, DDPG, ...

        self.nof_generations=nof_generations #number of generations for the GA

        self.pop_size=pop_size #population size for the GA

        self.pop_fitness=np.zeros(shape=(pop_size)) #fitness of all individuals
        self.pop_cum_fitness=np.zeros(shape=(pop_size)) #cumulative fitness for roulette wheel

        self.nof_elites = nof_elites

        self.crossover_rate=crossover_rate
        self.mutation_prob=mutation_prob

        self.action_type=action_type
        self.env=env
        self.test_env=test_env
        self.opt_func=opt_func
        self.device=device


    def get_GeneKeys(self):
        """
        :return: List of parameters for the RL model specified with "self.model_name"
        """

        if(self.model_name=="DQN"):
            parameter_list=["gamma","learning_rate","hidden_layers","nodes_per_layer","batch_size","step_size",
                            "test_iteration"]
            return parameter_list

        elif(self.model_name=="DDPG"):
            parameter_list = ["gamma", "learning_rate", "hidden_layers", "nodes_per_layer", "batch_size", "step_size",
                              "actor_learning_rate","critic_learning_rate","alpha_reward","beta_reward","gamma_reward",
                              "test_iteration"]
            return parameter_list

        elif (self.model_name == "TRPO"):
            parameter_list = ["gamma", "learning_rate", "hidden_layers", "nodes_per_layer", "batch_size", "step_size",
                              "actor_learning_rate", "critic_learning_rate", "alpha_reward", "beta_reward",
                              "gamma_reward","test_iteration"]
            return parameter_list
        elif (self.model_name == "ACKTR"):
            parameter_list = ["gamma", "learning_rate", "hidden_layers", "nodes_per_layer", "batch_size", "step_size",
                              "actor_learning_rate", "critic_learning_rate", "alpha_reward", "beta_reward",
                              "gamma_reward","epsilon","trajectory_size","max_kl","test_iteration"]
            return parameter_list

        elif (self.model_name == "A2C"):
            parameter_list = ["gamma", "learning_rate", "hidden_layers", "nodes_per_layer", "batch_size", "step_size",
                              "actor_learning_rate", "critic_learning_rate", "alpha_reward", "beta_reward",
                              "gamma_reward", "epsilon", "trajectory_size", "max_kl", "test_iteration"]
            return parameter_list
        else:
            print("RL Model Could Not Found")


    def RandomGene(self,gene_key):
        """
        :param gene_key: name of an hyper-parameter for the specified RL
        :return: random value for the hyper-parameter from its possible values specified in "self.PossibleGenesDict"
        """
        gene_index=np.random.randint(0, len(self.PossibleGenesDict[gene_key]))
        return self.PossibleGenesDict[gene_key][gene_index]


    def CreateRandomIndividual(self):
        """
        :return:  random chromosome "chr" for the specified RL
        -->e.g for DQN: chr ={'gamma': 0.05099999999999999,
                         'learning_rate': 0.08099999999999999,
                         'hidden_layers': 2,
                         'nodes_per_layer': 55,
                         'batch_size': 128,
                         'step_size': 2.0,
                         'test_iteration': 10000}
        """

        gene_keys=self.get_GeneKeys()
        chr={}
        for gene_key in gene_keys:
            chr[gene_key]=self.RandomGene(gene_key)
        return chr


    def InstantiateRandomPopulation(self):
        """
        Instantiates random population with "pop_size" number of random individuals for the specified RL
        :return:
        """
        for i in range(self.pop_size):
            self.population.append(self.CreateRandomIndividual())



    def CalculateFitness(self,chr,):

        """
        :param chr: chromosome (dictionary with each key corresponding to an appropriate hyper parameter for
        the specified RL)
        -->e.g for DQN: chr ={'gamma': 0.05099999999999999,
                         'learning_rate': 0.08099999999999999,
                         'hidden_layers': 2,
                         'nodes_per_layer': 55,
                         'batch_size': 128,
                         'step_size': 2.0,
                         'test_iteration': 10000}
        :return: fitness of the given chromosome "chr" calculated with the RL
        """


        if(self.model_name=="DQN"):
            fitness=1 #DQN Fitness Function
            return fitness

        elif (self.model_name == "DDPG"):
            #"batch_size", "step_size",
    #                           "actor_learning_rate","critic_learning_rate","alpha_reward","beta_reward","gamma_reward",
    #                           "test_iteration"]
            featurelist = [chr['nodes_per_layer']]*(chr['hidden_layers'] + 1)
            print(featurelist)
            fitness = ddpg.run_ddpq("Discrete",self.env,self.test_env,chr['hidden_layers'],featurelist,self.device, chr['gamma'],"LM", chr['batch_size'], chr['step_size'], chr['actor_learning_rate'], chr['critic_learning_rate'],
             chr['alpha_reward'], chr['beta_reward'], chr['gamma_reward'])
            print(fitness)
            return fitness

        elif (self.model_name == "TRPO"):
            fitness = 1  # TRPO Fitness Function
            return fitness

        elif (self.model_name == "ACKTR"):
            fitness = 1  # ACKTR Fitness Function
            return fitness

        elif (self.model_name == "A2C"):
            fitness = 1  # A2C Fitness Function
            return fitness

        else:
            print("RL Model Could Not Found")


    def CalculateCumulativeFitness(self):

        """
        Calculates cumulative fitness for "self.pop_cum_fitness". Where each cell  "self.pop_cum_fitness" correspond to
    the sum of fitness values of individuals from "self.population" upto and including the cell index.
        :return:
        """
        self.pop_cum_fitness[0] = self.pop_fitness[0]
        for i in range(self.pop_size-1):
            self.pop_cum_fitness[i+1]=self.pop_cum_fitness[i]+self.pop_fitness[i+1]
        self.pop_cum_fitness = self.pop_cum_fitness / self.pop_cum_fitness[-1]

    def RouletteSelect(self):
        """
        :return: Fitness proportional roulette wheen selection of a chromosome
        """
        rn=np.random.rand()
        for i in range(self.pop_size):
            if (rn<self.pop_cum_fitness[i]):
                return self.population[i]

    def RouletteSelect_Crossover_Mutate(self):
        """
        :return: chromosome where crossover (with crossover rate "self.crossover_rate") and mutation (with mutation
    probability "self.mutation_prob") is applied.
        """

        rn = np.random.rand()
        chr1 = copy.copy(self.RouletteSelect())
        gene_keys = self.get_GeneKeys()

        if (rn<self.crossover_rate):
            chr2 = copy.copy(self.RouletteSelect())

            preserve_from=np.random.randint(0,len(chr1)-1)
            for gene_key in gene_keys[0:preserve_from]:
                chr1[gene_key]=chr2[gene_key]

        for gene_key in gene_keys:
            if(np.random.rand()<self.mutation_prob):
                chr1[gene_key] = self.RandomGene(gene_key)
        return chr1


    def Elitist(self):
        """
        Directly passes "self.nof_elites" number of elites to next generation and logs the best fitness on current
    generation to "self.fitness_log". Also best individual "self.best_chr" is updated.
        :return:
        """


        pop_fitness_copy = copy.copy(self.pop_fitness)

        fitness_floor = np.min(pop_fitness_copy) - 1

        elite_indexes=[]
        for i in range(self.nof_elites):
            elite_indexes.append(np.argmax(pop_fitness_copy))
            pop_fitness_copy[elite_indexes[i]] = fitness_floor
            self.next_population.append(self.population[elite_indexes[i]])

        self.fitness_log.append(self.pop_fitness[elite_indexes[0]])
        self.best_chrm=self.next_population[0]


    def AdvenceGeneration(self):
        """
        Elites are selected and transferred to next generation, remaining slots on the next population are filled with
    mutated offsprings.
        :return:
        """

        self.Elitist()
        for i in range(self.pop_size-self.nof_elites):
            self.next_population.append(self.RouletteSelect_Crossover_Mutate())
        self.population=copy.copy(self.next_population)
        self.next_population=[]


    def Run(self,numProcesses,numThreads):
        """
        Run the Genetic Algorithm with the specified parameters and RL.
        :return: best individual "self.best_chr" at the last generation and fitness log of solutions "self.fitness_log"
    throughout the generations. With "mp.Pool" fitness for each individual is calculated in parallel.
        """

        pool = mp.Pool(mp.cpu_count())

        self.InstantiateRandomPopulation()

        for generation in range(self.nof_generations):

            self.pop_fitness=\
                np.array(pool.map(self.CalculateFitness, [chr for chr in self.population]))

            self.CalculateCumulativeFitness()
            self.AdvenceGeneration()

        pool.close()

        return self.best_chrm,self.fitness_log

