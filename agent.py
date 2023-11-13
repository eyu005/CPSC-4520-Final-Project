import math
import random
import sys

class Agent:
    def __init__(self, agentID, birthday, cell, configuration):
        self.ID = agentID
        self.born = birthday
        self.cell = cell

        self.sugarMetabolism = configuration["sugarMetabolism"]
        self.spiceMetabolism = configuration["spiceMetabolism"]
        self.movement = configuration["movement"]
        self.vision = configuration["vision"]
        self.sugar = configuration["sugar"]
        self.spice = configuration["spice"]
        self.startingSugar = configuration["sugar"]
        self.startingSpice = configuration["spice"]
        self.maxAge = configuration["maxAge"]
        self.sex = configuration["sex"]
        self.fertilityAge = configuration["fertilityAge"]
        self.infertilityAge = configuration["infertilityAge"]
        self.tags = configuration["tags"]
        self.aggressionFactor = configuration["aggressionFactor"]
        self.tradeFactor = configuration["tradeFactor"]
        self.lookaheadFactor = configuration["lookaheadFactor"]
        self.lendingFactor = configuration["lendingFactor"]
        self.fertilityFactor = configuration["fertilityFactor"]
        self.baseInterestRate = configuration["baseInterestRate"]
        self.loanDuration = configuration["loanDuration"]
        self.maxFriends = configuration["maxFriends"]
        self.wealth = configuration["sugar"] + configuration["spice"]
        self.seed = configuration["seed"]
        self.inheritancePolicy = configuration["inheritancePolicy"]
        self.startingImmuneSystem = configuration["immuneSystem"]
        self.immuneSystem = configuration["immuneSystem"]
<<<<<<< HEAD
        self.decisionModelFactor = configuration["decisionModelFactor"]
        self.selfishnessFactor = configuration["selfishnessFactor"]
        self.decisionModel = configuration["decisionModel"]
=======
        self.ethicalFactor = configuration["ethicalFactor"]
>>>>>>> 30f2bf4 (Update: adding movement as a separate mechanic)

        self.alive = True
        self.age = 0
        self.cellsInVision = []
        self.neighborhood = []
        self.lastMoved = -1
        self.vonNeumannNeighbors = {"north": None, "south": None, "east": None, "west": None}
        self.mooreNeighbors = {"north": None, "northeast": None, "northwest": None, "south": None, "southeast": None, "southwest": None, "east": None, "west": None}
        self.socialNetwork = {"father": None, "mother": None, "children": [], "friends": [], "creditors": [], "debtors": []}
        self.diseases = []
        self.fertile = False
        self.tribe = self.findTribe()
        self.timestep = birthday
        self.marginalRateOfSubstitution = 1
        self.tagZeroes = 0
        self.sugarMeanIncome = 1
        self.spiceMeanIncome = 1
        self.nice = 0

    def addChildToCell(self, mate, cell, childConfiguration):
        sugarscape = self.cell.environment.sugarscape
        childID = sugarscape.generateAgentID()
        child = Agent(childID, self.timestep, cell, childConfiguration)
        child.gotoCell(cell)
        sugarscape.addAgent(child)
        child.collectResourcesAtCell()
        if self.sex == "female":
            child.setMother(self)
            child.setFather(mate)
        else:
            child.setFather(self)
            child.setMother(mate)
        return child

    def addAgentToSocialNetwork(self, agent):
        agentID = agent.ID
        if agentID in self.socialNetwork:
            return
        self.socialNetwork[agentID] = {"agent": agent, "lastSeen": self.lastMoved, "timesVisited": 1, "timesReproduced": 0,
                                         "timesTraded": 0, "timesLoaned": 0, "marginalRateOfSubstitution": 0}

    def addLoanToAgent(self, agent, timestep, sugarPrincipal, sugarLoan, spicePrincipal, spiceLoan, duration):
        agentID = agent.ID
        if agentID not in self.socialNetwork:
            self.addAgentToSocialNetwork(agent)
        self.socialNetwork[agentID]["timesLoaned"] += 1
        agent.addLoanFromAgent(self, timestep, sugarLoan, spiceLoan, duration)
        loan = {"creditor": self.ID, "debtor": agentID, "sugarLoan": sugarLoan, "spiceLoan": spiceLoan, "loanDuration": duration,
                "loanOrigin": timestep}
        self.socialNetwork["debtors"].append(loan)
        self.sugar -= sugarPrincipal
        self.spice -= spicePrincipal
        agent.sugar = agent.sugar + sugarPrincipal
        agent.spice = agent.spice + spicePrincipal

    def addLoanFromAgent(self, agent, timestep, sugarLoan, spiceLoan, duration):
        agentID = agent.ID
        if agentID not in self.socialNetwork:
            self.addAgentToSocialNetwork(agent)
        self.socialNetwork[agentID]["timesLoaned"] += 1
        loan = {"creditor": agentID, "debtor": self.ID, "sugarLoan": sugarLoan, "spiceLoan": spiceLoan, "loanDuration": duration,
                "loanOrigin": timestep}
        self.socialNetwork["creditors"].append(loan)

    def calculateMarginalRateOfSubstitution(self, sugar, spice):
        spiceNeed = spice / self.spiceMetabolism if self.spiceMetabolism > 0 else 1
        sugarNeed = sugar / self.sugarMetabolism if self.sugarMetabolism > 0 else 1
        # If no sugar or no spice, make missing resource the maximum need in MRS
        if spiceNeed == 0:
            return self.spiceMetabolism
        elif sugarNeed == 0:
            return 1 / self.sugarMetabolism
        return spiceNeed / sugarNeed

    def calculateWelfare(self, sugarReward, spiceReward):
        totalMetabolism = self.sugarMetabolism + self.spiceMetabolism
        sugarMetabolismProportion = 0
        spiceMetabolismProportion = 0
        if totalMetabolism != 0:
            sugarMetabolismProportion = self.sugarMetabolism / totalMetabolism
            spiceMetabolismProportion = self.spiceMetabolism / totalMetabolism

        sugarLookahead = self.sugarMetabolism * self.lookaheadFactor
        spiceLookahead = self.spiceMetabolism * self.lookaheadFactor
        totalSugar = (self.sugar + sugarReward) - sugarLookahead
        totalSpice = (self.spice + spiceReward) - spiceLookahead
        if totalSugar < 0:
            totalSugar = 0
        if totalSpice < 0:
            totalSpice = 0

        welfare = (totalSugar ** sugarMetabolismProportion) * (totalSpice ** spiceMetabolismProportion)
        if self.tags != None and len(self.tags) > 0:
            # Tribe could have changed since last timestep, so recheck
            self.tribe = self.findTribe()
            fractionZeroesInTags = self.tagZeroes / len(self.tags)
            fractionOnesInTags = 1 - fractionZeroesInTags
            spiceMetabolism = self.spiceMetabolism if self.spiceMetabolism != 0 else 1
            sugarMetabolism = self.sugarMetabolism if self.sugarMetabolism != 0 else 1
            tagPreferences = (self.sugarMetabolism * fractionZeroesInTags) + (self.spiceMetabolism * fractionOnesInTags)
            if tagPreferences == 0:
                tagPreferences = 1
            tagPreferencesSugar = (self.sugarMetabolism / tagPreferences) * fractionZeroesInTags
            tagPreferencesSpice = (self.spiceMetabolism / tagPreferences) * fractionOnesInTags
            welfare = (totalSugar ** tagPreferencesSugar) * (totalSpice ** tagPreferencesSpice)
        return welfare
    
    def canReachCell(self, cell):
        if self.movement >= self.vision:
            for foundCell in self.cellsInMovement:
                if foundCell["cell"] == cell:
                    return True
            return False
        if self.vision > self.movement:
            for foundCell in self.cellsInVision:
                if foundCell["distance"] <= self.movement: 
                    if foundCell["cell"] == cell:
                        return True
                    else:
                        return False
                else:
                    return False
            return False

    def catchDisease(self, disease):
        diseaseID = disease.ID
        for currDisease in self.diseases:
            currDiseaseID = currDisease["disease"].ID
            # If currently sick with this disease, do not contract it again
            if diseaseID == currDiseaseID:
                return
        diseaseInImmuneSystem = self.findNearestHammingDistanceInDisease(disease)
        hammingDistance = diseaseInImmuneSystem["distance"]
        # If immune to disease, do not contract it
        if hammingDistance == 0:
            return
        startIndex = diseaseInImmuneSystem["start"]
        endIndex = diseaseInImmuneSystem["end"]
        caughtDisease = {"disease": disease, "startIndex": startIndex, "endIndex": endIndex}
        self.diseases.append(caughtDisease)
        self.updateDiseaseEffects(disease)
        disease.agent = self

    def collectResourcesAtCell(self):
        if self.cell != None:
            sugarCollected = self.cell.currSugar
            spiceCollected = self.cell.currSpice
            self.sugar += sugarCollected
            self.spice += spiceCollected
            self.wealth += sugarCollected + spiceCollected
            self.updateMeanIncome(sugarCollected, spiceCollected)
            self.cell.doSugarProductionPollution(sugarCollected)
            self.cell.doSpiceProductionPollution(spiceCollected)
            self.cell.resetSugar()
            self.cell.resetSpice()

    def defaultOnLoan(self, loan):
        for creditor in self.socialNetwork["creditors"]:
            continue
        return

    def doAging(self):
        if self.alive == False:
            return
        self.age += 1
        # Die if reached max age and if not infinitely-lived
        if self.age >= self.maxAge and self.maxAge != -1:
            self.doDeath()

    def doCombat(self, cell):
        prey = cell.agent
        if prey != None and prey != self:
            maxCombatLoot = self.cell.environment.maxCombatLoot
            preySugar = prey.sugar
            preySpice = prey.spice
            sugarLoot = min(maxCombatLoot, preySugar)
            spiceLoot = min(maxCombatLoot, preySpice)
            self.sugar += sugarLoot
            self.spice += spiceLoot
            self.wealth = self.sugar + self.spice
            prey.sugar = preySugar - sugarLoot
            prey.spice = preySpice - spiceLoot
            prey.doDeath()
        self.gotoCell(cell)

    def doDeath(self):
        self.alive = False
        self.resetCell()
        self.doInheritance()

    def doDisease(self):
        diseases = self.diseases
        for diseaseRecord in diseases:
            diseaseTags = diseaseRecord["disease"].tags
            start = diseaseRecord["startIndex"]
            end = diseaseRecord["endIndex"] + 1
            immuneResponse = [self.immuneSystem[i] for i in range(diseaseRecord["startIndex"], diseaseRecord["endIndex"] + 1)]
            i = start
            j = 0
            for i in range(len(diseaseTags)):
                if immuneResponse[i] != diseaseTags[i]:
                    self.immuneSystem[start + i] = diseaseTags[i]
                    break
            immuneResponseCheck = [self.immuneSystem[i] for i in range(diseaseRecord["startIndex"], diseaseRecord["endIndex"] + 1)]
            if diseaseTags == immuneResponseCheck:
                self.diseases.remove(diseaseRecord)
                self.updateDiseaseEffects(diseaseRecord["disease"])

        diseaseCount = len(self.diseases)
        if diseaseCount == 0:
            return
        neighborCells = self.cell.neighbors
        neighbors = []
        for neighborCell in neighborCells:
            neighbor = neighborCell.agent
            if neighbor != None and neighbor.isAlive() == True:
                neighbors.append(neighbor)
        random.shuffle(neighbors)
        for neighbor in neighbors:
            self.spreadDisease(neighbor, self.diseases[random.randrange(diseaseCount)]["disease"])

    def doInheritance(self):
        if self.inheritancePolicy == "none":
            return
        # Provide inheritance for living children/sons/daughters/friends
        livingChildren = []
        livingSons = []
        livingDaughters = []
        livingFriends = []
        for child in self.socialNetwork["children"]:
            if child.isAlive() == True:
                livingChildren.append(child)
                childSex = child.sex
                if childSex == "male":
                    livingSons.append(child)
                elif childSex == "female":
                    livingDaughters.append(child)
        for friend in self.socialNetwork["friends"]:
            if friend["friend"].isAlive() == True:
                livingFriends.append(friend["friend"])

        if self.inheritancePolicy == "children" and len(livingChildren) > 0:
            sugarInheritance = round(self.sugar / len(livingChildren), 2)
            spiceInheritance = round(self.spice / len(livingChildren), 2)
            for child in livingChildren:
                child.sugar = child.sugar + sugarInheritance
                child.spice = child.spice + spiceInheritance
        elif self.inheritancePolicy == "sons" and len(livingSons) > 0:
            sugarInheritance = round(self.sugar / len(livingSons), 2)
            spiceInheritance = round(self.spice / len(livingSons), 2)
            for son in livingSons:
                son.sugar = son.sugar + sugarInheritance
                son.spice = son.spice + spiceInheritance
        elif self.inheritancePolicy == "daughters" and len(livingDaughters) > 0:
            sugarInheritance = round(self.sugar / len(livingDaughters), 2)
            spiceInheritance = round(self.spice / len(livingDaughters), 2)
            for daughter in livingDaughters:
                daughter.sugar = daughter.sugar + sugarInheritance
                daughter.spice = daughter.spice + spiceInheritance
        elif self.inheritancePolicy == "friends" and len(livingFriends) > 0:
            sugarInheritance = round(self.sugar / len(livingFriends), 2)
            spiceInheritance = round(self.spice / len(livingFriends), 2)
            for friend in livingFriends:
                friend.sugar = friend.sugar + sugarInheritance
                friend.spice = friend.spice + spiceInheritance
        self.sugar = 0
        self.spice = 0

    def doLending(self):
        self.updateLoans()
        # If not a lender, skip lending
        if self.lendingFactor == 0:
            return
        # Fertile and not enough excess wealth to be a lender
        elif self.isFertile() == True and (self.sugar <= self.startingSugar or self.spice <= self.startingSpice):
            return
        # Too young to reproduce, skip lending
        elif self.age < self.fertilityAge:
            return
        # Maximum interest rate of 100%
        interestRate = min(1, self.lendingFactor * self.baseInterestRate)
        neighbors = self.cell.findNeighborAgents()
        borrowers = []
        for neighbor in neighbors:
            if neighbor.isAlive() == False:
                continue
            if neighbor.age >= neighbor.fertilityAge and neighbor.age < neighbor.infertilityAge and neighbor.isFertile() == False:
                borrowers.append(neighbor)
        random.shuffle(borrowers)
        for borrower in borrowers:
            maxSugarLoan = self.sugar / 2
            maxSpiceLoan = self.spice / 2
            if self.isFertile() == True:
                maxSugarLoan = max(0, self.sugar - self.startingSugar)
                maxSpiceLoan = max(0, self.spice - self.startingSpice)
            # If not enough excess wealth to lend, stop lending
            if maxSugarLoan == 0 and maxSpiceLoan == 0:
                return
            sugarLoanNeed = max(0, borrower.startingSugar - borrower.sugar)
            spiceLoanNeed = max(0, borrower.startingSpice - borrower.spice)
            # Find sugar and spice loans, rounded to 2 decimal places
            sugarLoanPrincipal = round(min(maxSugarLoan, sugarLoanNeed), 2)
            spiceLoanPrincipal = round(min(maxSpiceLoan, spiceLoanNeed), 2)
            sugarLoanAmount = round(sugarLoanPrincipal + (sugarLoanPrincipal * interestRate), 2)
            spiceLoanAmount = round(spiceLoanPrincipal + (spiceLoanPrincipal * interestRate), 2)
            # If no loan needed within significant figures or lender excess resources exhausted
            if (sugarLoanNeed == 0 and spiceLoanNeed == 0) or (sugarLoanAmount == 0 and spiceLoanAmount == 0):
                continue
            # If lending would cause lender to starve, skip lending to potential borrower
            elif self.sugar - sugarLoanPrincipal <= self.sugarMetabolism or self.spice - spiceLoanPrincipal <= self.spiceMetabolism:
                continue
            elif borrower.isCreditWorthy(sugarLoanAmount, spiceLoanAmount, self.loanDuration) == True:
                print("Agent {0} lending [{1},{2}] to agent {3} for {4} timesteps with total loan valued at [{5},{6}]".format(str(self), sugarLoanPrincipal, spiceLoanPrincipal, str(borrower), self.loanDuration, sugarLoanAmount, spiceLoanAmount))
                self.addLoanToAgent(borrower, self.lastMoved, sugarLoanPrincipal, sugarLoanAmount, spiceLoanPrincipal, spiceLoanAmount, self.loanDuration)

    def doMetabolism(self):
        if self.alive == False:
            return
        self.sugar -= self.sugarMetabolism
        self.spice -= self.spiceMetabolism
        self.cell.doSugarConsumptionPollution(self.sugarMetabolism)
        self.cell.doSpiceConsumptionPollution(self.spiceMetabolism)
        if (self.sugar < 1 and self.sugarMetabolism > 0) or (self.spice < 1 and self.spiceMetabolism > 0):
            self.doDeath()

    def doReproduction(self):
        # Agent marked for removal or not interested in reproduction should not reproduce
        if self.alive == False or self.isFertile() == False:
            return
        neighborCells = self.cell.neighbors
        random.shuffle(neighborCells)
        emptyCells = self.findEmptyNeighborCells()
        for neighborCell in neighborCells:
            neighbor = neighborCell.agent
            if neighbor != None:
                neighborCompatibility = self.isNeighborReproductionCompatible(neighbor)
                emptyCellsWithNeighbor = emptyCells + neighbor.findEmptyNeighborCells()
                random.shuffle(emptyCellsWithNeighbor)
                if self.isFertile() == True and neighborCompatibility == True and len(emptyCellsWithNeighbor) != 0:
                    print("blegh")
                    emptyCell = emptyCellsWithNeighbor.pop()
                    while emptyCell.agent != None and len(emptyCellsWithNeighbor) != 0:
                        emptyCell = emptyCellsWithNeighbor.pop()
                    # If no adjacent empty cell is found, skip reproduction with this neighbor
                    if emptyCell.agent != None:
                        continue
                    childEndowment = self.findChildEndowment(neighbor)
                    child = self.addChildToCell(neighbor, emptyCell, childEndowment)
                    self.socialNetwork["children"].append(child)
                    childID = child.ID
                    neighborID = neighbor.ID
                    self.addAgentToSocialNetwork(child)
                    neighbor.addAgentToSocialNetwork(child)
                    neighbor.updateTimesVisitedWithAgent(self, self.lastMoved)
                    neighbor.updateTimesReproducedWithAgent(self, self.lastMoved)
                    self.updateTimesReproducedWithAgent(neighbor, self.lastMoved)

                    sugarCost = round(self.startingSugar / (self.fertilityFactor * 2), 2)
                    spiceCost = round(self.startingSpice / (self.fertilityFactor * 2), 2)
                    mateSugarCost = round(neighbor.startingSugar / (neighbor.fertilityFactor * 2), 2)
                    mateSpiceCost = round(neighbor.startingSpice / (neighbor.fertilityFactor * 2), 2)
                    self.sugar -= sugarCost
                    self.spice -= spiceCost
                    neighbor.sugar = neighbor.sugar - mateSugarCost
                    neighbor.spice = neighbor.spice - mateSpiceCost

    def doTagging(self):
        if self.tags == None or self.alive == False:
            return
        neighborCells = self.cell.neighbors
        random.shuffle(neighborCells)
        for neighborCell in neighborCells:
            neighbor = neighborCell.agent
            if neighbor != None:
                position = random.randrange(len(self.tags))
                neighbor.flipTag(position, self.tags[position])
                neighbor.tribe = neighbor.findTribe()

    def doTimestep(self, timestep):
        self.timestep = timestep
        # Prevent dead or already moved agent from moving
        if self.alive == True and self.cell != None and self.lastMoved != self.timestep:
            self.lastMoved = self.timestep
            self.moveToBestCell()
            self.updateNeighbors()
            self.collectResourcesAtCell()
            self.doMetabolism()
            # If dead from metabolism, skip remainder of timestep
            if self.alive == False:
                return
            self.doTagging()
            self.doTrading()
            self.doReproduction()
            self.doLending()
            self.doDisease()
            self.doAging()

    def doTrading(self):
        # If not a trader, skip trading
        if self.tradeFactor == 0:
            return
        self.findMarginalRateOfSubstitution()
        neighborCells = self.cell.neighbors
        traders = []
        for neighborCell in neighborCells:
            neighbor = neighborCell.agent
            if neighbor != None and neighbor.isAlive() == True:
                neighborMRS = neighbor.marginalRateOfSubstitution
                if neighborMRS != self.marginalRateOfSubstitution:
                    traders.append(neighbor)
        random.shuffle(traders)
        for trader in traders:
            spiceSeller = None
            sugarSeller = None
            tradeFlag = True
            transactions = 0

            while tradeFlag == True:
                traderMRS = trader.marginalRateOfSubstitution
                # If both trying to sell the same commodity, stop trading
                if traderMRS >= 1 and self.marginalRateOfSubstitution >= 1:
                    tradeFlag = False
                    continue
                elif traderMRS < 1 and self.marginalRateOfSubstitution < 1:
                    tradeFlag = False
                    continue
                elif traderMRS == self.marginalRateOfSubstitution:
                    tradeFlag = False
                    continue

                # MRS > 1 indicates the agent has less need of spice and should become the spice seller
                if traderMRS > self.marginalRateOfSubstitution:
                    spiceSeller = trader
                    sugarSeller = self
                else:
                    spiceSeller = self
                    sugarSeller = trader
                spiceSellerMRS = spiceSeller.marginalRateOfSubstitution
                sugarSellerMRS = sugarSeller.marginalRateOfSubstitution

                # Find geometric mean of spice and sugar seller MRS for trade price, rounded to 2 decimal places
                tradePrice = round(math.sqrt(spiceSellerMRS * sugarSellerMRS), 2)
                sugarPrice = 0
                spicePrice = 0
                # Set proper highest value commodity based on trade price
                if tradePrice < 1:
                    spicePrice = 1
                    sugarPrice = tradePrice
                else:
                    spicePrice = tradePrice
                    sugarPrice = 1

                # If trade would be lethal, skip it
                if spiceSeller.spice - spicePrice < spiceSeller.spiceMetabolism or sugarSeller.sugar - sugarPrice < sugarSeller.sugarMetabolism:
                    tradeFlag = False
                    continue
                spiceSellerNewMRS = spiceSeller.calculateMarginalRateOfSubstitution(spiceSeller.sugar + sugarPrice, spiceSeller.spice - spicePrice)
                sugarSellerNewMRS = sugarSeller.calculateMarginalRateOfSubstitution(sugarSeller.sugar - sugarPrice, sugarSeller.spice + spicePrice)

                # Calculate absolute difference from perfect spice/sugar parity in MRS and change in agent welfare
                betterSpiceSellerMRS = abs(1 - spiceSellerMRS) > abs(1 - spiceSellerNewMRS)
                betterSugarSellerMRS = abs(1 - sugarSellerMRS) > abs(1 - sugarSellerNewMRS)
                betterSpiceSellerWelfare = spiceSeller.calculateWelfare(sugarPrice, (-1 * spicePrice)) >= spiceSeller.calculateWelfare(0, 0)
                betterSugarSellerWelfare = sugarSeller.calculateWelfare((-1 * sugarPrice), spicePrice) >= sugarSeller.calculateWelfare(0, 0)
                # If either MRS or welfare is improved, mark the trade as better for agent
                betterForSpiceSeller = betterSpiceSellerMRS or betterSpiceSellerWelfare
                betterForSugarSeller = betterSugarSellerMRS or betterSugarSellerWelfare

                # Check that spice seller's new MRS does not cross over sugar seller's new MRS
                # Evaluates to False for successful trades
                checkForMRSCrossing = spiceSellerNewMRS < sugarSellerNewMRS
                if betterForSpiceSeller == True and betterForSugarSeller == True and checkForMRSCrossing == False:
                    print("Agent {0} trading {1} spice for {2} sugar from agent {3}".format(str(spiceSeller), spicePrice, sugarPrice, str(sugarSeller)))
                    spiceSeller.sugar += sugarPrice
                    spiceSeller.spice -= spicePrice
                    sugarSeller.sugar -= sugarPrice
                    sugarSeller.spice += spicePrice
                    spiceSeller.findMarginalRateOfSubstitution()
                    sugarSeller.findMarginalRateOfSubstitution()
                    transactions += 1
                else:
                    tradeFlag = False
                    continue
            # If a trade occurred, log it
            if spiceSeller != None and sugarSeller != None:
                trader.updateTimesTradedWithAgent(self, self.lastMoved, transactions)
                self.updateTimesTradedWithAgent(trader, self.lastMoved, transactions)

    def findAgentWealthAtCell(self, cell):
        agent = cell.agent
        if agent == None:
            return 0
        else:
            return agent.wealth

    '''
    We have concluded that intensity, duration, and certainty are correct. We need to normalize/scale them to either TTL or total resource value.
    Certainty will change once we implement a separation of movement and vision.
    Currently proximity is 1, because if you can see it, you can eat it. Again, this will change when we change movement from vision. (1/distance in time steps)
    Fecundity/purity are a single magical variable named futureBliss. The futureBliss variable represents the probability of future pleasure.
    Extent is # of agents in our vision.
    We will assume omniscience within our own neighborhood.
    utilicalcSugar:
    a.	Intensity: [0 : 1] (1/1+daysToDeath)
    b.	Duration: [0 : 1] [(cell site wealth / agent metabolism) / maxSiteWealth], which is rational
    c.  Certainty: [1 : 1] if agent can reach move cell, [0 : 0] otherwise
    d.  Proximity: [0 : 1] the (1/distance in time steps), which is currently 1
    e.  FutureBliss: [0 : 1] probability of immediate (or limited by computational horizon) future pleasure subsequent to this action
    f.  Extent: (0 : 1] number of agents in neighborhood  / #agents_visible_in_maxVision
    utility_of_cell = certainty * proximity * (intensity + duration + discount * futureBliss * futureReward??? + extent)
    We may wish to weight the variables inside the parenthesis based on some relative importance that we will make up, based on how we think Bentham thought.
    And of course, we will be right.
    '''
    def findBenthamActUtilitarianValueOfCell(self, cell):
        # TODO: Consider neighbors of the potential cell for trading, lending, and reproduction (which generate nice)
        cellNeighborAgents = cell.findNeighborAgents()
        cellSiteWealth = cell.currSugar + cell.currSpice
        cellMaxSiteWealth = cell.maxSugar + cell.maxSpice
        cellValue = 0
        for agent in self.neighborhood:
            timestepDistance = 1
            agentVision = agent.vision
            agentMovement = agent.movement
            agentMetabolism = agent.sugarMetabolism + agent.spiceMetabolism
            # If agent does not have metabolism, set duration to seemingly infinite
            cellDuration = cellSiteWealth / agentMetabolism if agentMetabolism > 0 else 0
            certainty = 1 if agent.canReachCell(cell) == True else 0
            proximity = 1 / timestepDistance
            intensity = 1 / (1 + agent.findDaysToDeath())
            # if metabolism == 0 case
            duration = cellDuration / cellMaxSiteWealth if cellMaxSiteWealth > 0 else 0
            # Agent discount, futureBliss, and futureReward deal with purity and fecundity, not currently included
            discount = 0
            futureBliss = 0
            futureReward = 0
            # Assuming agent can only see in four cardinal directions
            extent = len(self.neighborhood) / (agentVision * 4) if agentVision > 0 else 1
            # If not the agent moving, consider these as opportunity costs
            if agent != self:
                intensity = -1 * intensity
                duration = -1 * duration
            agentValueOfCell = agent.ethicalFactor * (certainty * proximity * (intensity + duration + (discount * futureBliss * futureReward) + extent))
            cellValue += agentValueOfCell
        return cellValue

    def findBestCell(self):
      
        self.findCellsInVision()
        neighborhood = []
        for neighborCell in self.cellsInVision:
            neighbor = neighborCell["cell"].agent
            if neighbor != None and neighbor.isAlive() == True:
                neighborhood.append(neighbor)
        neighborhood.append(self)
        self.neighborhood = neighborhood
        retaliators = self.findRetaliatorsInVision()
        totalMetabolism = self.sugarMetabolism + self.spiceMetabolism
        sugarMetabolismProportion = 0
        spiceMetabolismProportion = 0
        if totalMetabolism != 0: 
            sugarMetabolismProportion = self.sugarMetabolism / totalMetabolism
            spiceMetabolismProportion = self.spiceMetabolism / totalMetabolism
        random.shuffle(self.cellsInVision)

        self.findCellsInMovement()
        random.shuffle(self.cellsInMovement)

        bestCell = None
        bestRange = max(self.cell.environment.height, self.cell.environment.width)
        bestWealth = 0
        agentX = self.cell.x
        agentY = self.cell.y
        combatMaxLoot = self.cell.environment.maxCombatLoot
        wraparound = self.vision + 1
        potentialCells = []
     
        for currCell in self.cellsInMovement:
            cell = currCell["cell"]
            travelDistance = currCell["distance"]

            if cell.isOccupied() == True and self.aggressionFactor == 0:
                continue
            cellSugar = cell.currSugar
            cellSpice = cell.currSpice
            prey = cell.agent
            # Avoid attacking agents from the same tribe
            if prey != None and prey.tribe == self.tribe:
                continue
            preyTribe = prey.tribe if prey != None else "empty"
            preyWealth = prey.wealth if prey != None else 0
            preySugar = prey.sugar if prey != None else 0
            preySpice = prey.spice if prey != None else 0
            # Aggression factor may lead agent to see more reward than possible meaning combat itself is a reward
            welfarePreySugar = self.aggressionFactor * min(combatMaxLoot, preySugar)
            welfarePreySpice = self.aggressionFactor * min(combatMaxLoot, preySpice)

            # Avoid attacking stronger agents
            if prey != None and preyWealth > self.wealth:
                continue

            cellWealth = 0
            # Modify value of cell relative to the metabolism needs of the agent
            welfare = self.calculateWelfare((cellSugar + welfarePreySugar), (cellSpice + welfarePreySpice))
            cellWealth = welfare / (1 + cell.currPollution)

            # Avoid attacking agents protected via retaliation
            if prey != None and retaliators[preyTribe] > self.wealth + cellWealth:
                continue

            if bestCell == None:
                bestCell = cell
                bestRange = travelDistance
                bestWealth = cellWealth

            # Select closest cell with the most resources
            if cellWealth > bestWealth or (cellWealth == bestWealth and travelDistance < bestRange):
                if prey != None and prey.wealth > self.wealth:
                    continue
                bestRange = travelDistance
                bestCell = cell
                bestWealth = cellWealth

            cellRecord = {"cell": cell, "wealth": cellWealth, "range": travelDistance}
            potentialCells.append(cellRecord)

<<<<<<< HEAD
        if self.decisionModelFactor > 0:
            bestCell = self.findBestEthicalCell(potentialCells, bestCell)
=======
        if self.ethicalFactor > 0:
            bestCell = self.findBestEthicalCell(potentialCells)
>>>>>>> 30f2bf4 (Update: adding movement as a separate mechanic)
        if bestCell == None:
            bestCell = self.cell
        '''
        if self.ethicalFactor == 0:
            print("Agent {0} moving to ({1},{2})".format(str(self), bestCell.x, bestCell.y))
        else:
            print("Agent {0} moving to ({1},{2})".format(str(self), bestCell.x, bestCell.y))
        '''
        return bestCell

    def findBestEthicalCell(self, cells):
        if len(cells) == 0:
            return None
        # Insertion sort of cells by wealth with range as a tiebreaker
        i = 0
        while i < len(cells):
            j = i
            while j > 0 and (cells[j - 1]["wealth"] > cells[j]["wealth"] or (cells[j - 1]["wealth"] == cells[j]["wealth"] and cells[j - 1]["range"] <= cells[j]["range"])):
                currCell = cells[j]
                cells[j] = cells[j - 1]
                cells[j - 1] = currCell
                j -= 1
            i += 1
        bestCell = None
        # TODO: From best to worst cell score, select cell that produces positive nice
        cells.reverse()
<<<<<<< HEAD
        if "all" in self.debug or "agent" in self.debug:
            self.printCellScores(cells)
        # If not an ethical agent, return top selfish choice
        if self.decisionModel == "none":
            return greedyBestCell

        # Calculate initial utility value calculation and naively select based on binary decision first
        if "benthamNoLookahead" in self.decisionModel:
            for cell in cells:
                ethicalScore = ethics.findBenthamNoLookaheadValueOfCell(self, cell["cell"])
                cell["wealth"] = ethicalScore
            for cell in cells:
                if cell["wealth"] > 0:
                    bestCell = cell["cell"]
                    break
        elif "benthamHalfLookahead" in self.decisionModel:
            for cell in cells:
                ethicalScore = ethics.findBenthamHalfLookaheadValueOfCell(self, cell["cell"])
                cell["wealth"] = ethicalScore
            for cell in cells:
                if cell["wealth"] > 0:
                    bestCell = cell["cell"]
                    break

        elif "altruisticHalfLookahead" in self.decisionModel:
            for cell in cells:
                ethicalScore = ethics.findAltruisticHalfLookaheadValueOfCell(self, cell["cell"])
                cell["wealth"] = ethicalScore
            for cell in cells:
                if cell["wealth"] > 0:
                    bestCell = cell["cell"]
                    break
        elif "egoisticHalfLookahead" in self.decisionModel:
            for cell in cells:
                ethicalScore = ethics.findEgoisticHalfLookaheadValueOfCell(self, cell["cell"])
                cell["wealth"] = ethicalScore
            for cell in cells:
                if cell["wealth"] > 0:
                    bestCell = cell["cell"]
                    break
        elif "egoisticNoLookahead" in self.decisionModel:
            for cell in cells:
                ethicalScore = ethics.findEgoisticNoLookaheadValueOfCell(self, cell["cell"])
                cell["wealth"] = ethicalScore
            for cell in cells:
                if cell["wealth"] > 0:
                    bestCell = cell["cell"]
                    break

        # If additional ordering consideration, select new best cell
        if "Top" in self.decisionModel:
            cells = self.sortCellsByWealth(cells)
            cells.reverse()
            if "all" in self.debug or "agent" in self.debug:
                self.printEthicalCellScores(cells)
            bestCell = cells[0]["cell"]

=======
        for cell in cells:
            ethicalScore = self.findBenthamActUtilitarianValueOfCell(cell["cell"])
            if ethicalScore > 0:
                bestCell = cell["cell"]
                break
>>>>>>> 30f2bf4 (Update: adding movement as a separate mechanic)
        if bestCell == None:
            bestCell = cells.pop()["cell"]
        return bestCell

    def findBestFriend(self):
        if self.tags == None:
            return None
        minHammingDistance = len(self.tags)
        bestFriend = None
        for friend in self.socialNetwork["friends"]:
            # If already a friend, update Hamming Distance
            if friend["hammingDistance"] < minHammingDistance:
                bestFriend = friend
                minHammingDistance = friend["hammingDistance"]
        return bestFriend

    def findCellsInVision(self):
        if self.vision > 0 and self.cell != None:
            northCells = [{"cell": self.cell.findNorthNeighbor(), "distance": 1}]
            southCells = [{"cell": self.cell.findSouthNeighbor(), "distance": 1}]
            eastCells = [{"cell": self.cell.findEastNeighbor(), "distance": 1}]
            westCells = [{"cell": self.cell.findWestNeighbor(), "distance": 1}]
            # Vision 1 accounted for in list setup
            for i in range(1, self.vision):
                northCells.append({"cell": northCells[-1]["cell"].findNorthNeighbor(), "distance": i + 1})
                southCells.append({"cell": southCells[-1]["cell"].findSouthNeighbor(), "distance": i + 1})
                eastCells.append({"cell": eastCells[-1]["cell"].findEastNeighbor(), "distance": i + 1})
                westCells.append({"cell": westCells[-1]["cell"].findWestNeighbor(), "distance": i + 1})
            self.cellsInVision = northCells + southCells + eastCells + westCells

    def findCellsInMovement(self):
        if self.movement > 0 and self.cell != None:
            northCells = [{"cell": self.cell.findNorthNeighbor(), "distance": 1}]
            southCells = [{"cell": self.cell.findSouthNeighbor(), "distance": 1}]
            eastCells = [{"cell": self.cell.findEastNeighbor(), "distance": 1}]
            westCells = [{"cell": self.cell.findWestNeighbor(), "distance": 1}]
            # Movement 1 accounted for in list setup
            for i in range(1, self.movement):
                northCells.append({"cell": northCells[-1]["cell"].findNorthNeighbor(), "distance": i + 1})
                southCells.append({"cell": southCells[-1]["cell"].findSouthNeighbor(), "distance": i + 1})
                eastCells.append({"cell": eastCells[-1]["cell"].findEastNeighbor(), "distance": i + 1})
                westCells.append({"cell": westCells[-1]["cell"].findWestNeighbor(), "distance": i + 1})
            self.cellsInMovement = northCells + southCells + eastCells + westCells

    def findChildEndowment(self, mate):
<<<<<<< HEAD
        parentEndowments = {
        "aggressionFactor": [self.aggressionFactor, mate.aggressionFactor],
        "baseInterestRate": [self.baseInterestRate, mate.baseInterestRate],
        "decisionModelFactor": [self.decisionModelFactor, mate.decisionModelFactor],
        "decisionModel": [self.decisionModel, mate.decisionModel],
        "fertilityAge": [self.fertilityAge, mate.fertilityAge],
        "fertilityFactor": [self.fertilityFactor, mate.fertilityFactor],
        "infertilityAge": [self.infertilityAge, mate.infertilityAge],
        "inheritancePolicy": [self.inheritancePolicy, mate.inheritancePolicy],
        "lendingFactor": [self.lendingFactor, mate.lendingFactor],
        "loanDuration": [self.loanDuration, mate.loanDuration],
        "lookaheadFactor": [self.lookaheadFactor, mate.lookaheadFactor],
        "maxAge": [self.maxAge, mate.maxAge],
        "maxFriends": [self.maxFriends, mate.maxFriends],
        "movement": [self.movement, mate.movement],
        "selfishnessFactor" : [self.selfishnessFactor, mate.selfishnessFactor],
        "spiceMetabolism": [self.spiceMetabolism, mate.spiceMetabolism],
        "sugarMetabolism": [self.sugarMetabolism, mate.sugarMetabolism],
        "sex": [self.sex, mate.sex],
        "tradeFactor": [self.tradeFactor, mate.tradeFactor],
        "vision": [self.vision, mate.vision]
        }
        childEndowment = {"seed": self.seed}
        randomNumberReset = random.getstate() 
        # Map configuration to a random number via hash to make random number generation independent of iteration order
        if self.childEndowmentHashes == None:
            self.childEndowmentHashes = {}
            for config in parentEndowments:
                hashed = hashlib.md5(config.encode())
                hashNum = int(hashed.hexdigest(), 16)
                self.childEndowmentHashes[config] = hashNum
=======
        parentSugarMetabolisms = [self.sugarMetabolism, mate.sugarMetabolism]
        parentSpiceMetabolisms = [self.spiceMetabolism, mate.spiceMetabolism]
        parentMovements = [self.movement, mate.movement]
        parentVisions = [self.vision, mate.vision]
        parentMaxAges = [self.maxAge, mate.maxAge]
        parentInfertilityAges = [self.infertilityAge, mate.infertilityAge]
        parentFertilityAges = [self.fertilityAge, mate.fertilityAge]
        parentSexes = [self.sex, mate.sex]
        parentAggressionFactors = [self.aggressionFactor, mate.aggressionFactor]
        parentTradeFactors = [self.tradeFactor, mate.tradeFactor]
        parentLookaheadFactors = [self.lookaheadFactor, mate.lookaheadFactor]
        parentLendingFactors = [self.lendingFactor, mate.lendingFactor]
        parentFertilityFactors = [self.fertilityFactor, mate.fertilityFactor]
        parentBaseInterestRates = [self.baseInterestRate, mate.baseInterestRate]
        parentLoanDuration = [self.loanDuration, mate.loanDuration]
        parentMaxFriends = [self.maxFriends, mate.maxFriends]
        parentEthicalFactors = [self.ethicalFactor, mate.ethicalFactor]
        # Each parent gives 1/2 their starting endowment for child endowment
        childStartingSugar = round((self.startingSugar / 2) + (mate.startingSugar / 2), 2)
        childStartingSpice = round((self.startingSpice / 2) + (mate.startingSpice / 2), 2)
>>>>>>> 30f2bf4 (Update: adding movement as a separate mechanic)

        childSugarMetabolism = parentSugarMetabolisms[random.randrange(2)]
        childSpiceMetabolism = parentSpiceMetabolisms[random.randrange(2)]
        childMovement = parentMovements[random.randrange(2)]
        childVision = parentVisions[random.randrange(2)]
        childMaxAge = parentMaxAges[random.randrange(2)]
        childInfertilityAge = parentInfertilityAges[random.randrange(2)]
        childFertilityAge = parentFertilityAges[random.randrange(2)]
        childFertilityFactor = parentFertilityFactors[random.randrange(2)]
        childSex = parentSexes[random.randrange(2)]
        childMaxFriends = parentMaxFriends[random.randrange(2)]
        childTags = []
        childImmuneSystem = []
        mateTags = mate.tags
        mismatchBits = [0, 1]
        if self.tags == None:
            childTags = None
        else:
            for i in range(len(self.tags)):
                if self.tags[i] == mateTags[i]:
                    childTags.append(self.tags[i])
                else:
                    childTags.append(mismatchBits[random.randrange(2)])
        mateStartingImmuneSystem = mate.startingImmuneSystem
        if self.startingImmuneSystem == None:
            childImmuneSystem = None
        else:
            for i in range(len(self.immuneSystem)):
                if self.startingImmuneSystem[i] == mateStartingImmuneSystem[i]:
                    childImmuneSystem.append(self.startingImmuneSystem[i])
                else:
                    childImmuneSystem.append(mismatchBits[random.randrange(2)])
        childAggressionFactor = parentAggressionFactors[random.randrange(2)]
        childTradeFactor = parentTradeFactors[random.randrange(2)]
        childLookaheadFactor = parentLookaheadFactors[random.randrange(2)]
        childLendingFactor = parentLendingFactors[random.randrange(2)]
        childBaseInterestRate = parentBaseInterestRates[random.randrange(2)]
        childLoanDuration = parentLoanDuration[random.randrange(2)]
        childEthicalFactor = parentEthicalFactors[random.randrange(2)]
        endowment = {"movement": childMovement, "vision": childVision, "maxAge": childMaxAge, "sugar": childStartingSugar,
                     "spice": childStartingSpice, "sex": childSex, "fertilityAge": childFertilityAge, "infertilityAge": childInfertilityAge, "tags": childTags,
                     "aggressionFactor": childAggressionFactor, "maxFriends": childMaxFriends, "seed": self.seed, "sugarMetabolism": childSugarMetabolism,
                     "spiceMetabolism": childSpiceMetabolism, "inheritancePolicy": self.inheritancePolicy, "tradeFactor": childTradeFactor,
                     "lookaheadFactor": childLookaheadFactor, "lendingFactor": childLendingFactor, "baseInterestRate": childBaseInterestRate,
                     "loanDuration": childLoanDuration, "immuneSystem": childImmuneSystem, "fertilityFactor": childFertilityFactor,
                     "ethicalFactor": childEthicalFactor}
        return endowment

    def findCurrentSpiceDebt(self):
        spiceDebt = 0
        for creditor in self.socialNetwork["creditors"]:
            spiceDebt += creditor["spiceLoan"] / creditor["loanDuration"]
        return spiceDebt

    def findCurrentSugarDebt(self):
        sugarDebt = 0
        for creditor in self.socialNetwork["creditors"]:
            sugarDebt += creditor["sugarLoan"] / creditor["loanDuration"]
        return sugarDebt

    def findDaysToDeath(self):
        # If no sugar or spice metabolism, set days to death for that resource to seemingly infinite
        sugarDaysToDeath = self.sugar / self.sugarMetabolism if self.sugarMetabolism > 0 else sys.maxsize
        spiceDaysToDeath = self.spice / self.spiceMetabolism if self.spiceMetabolism > 0 else sys.maxsize
        daysToDeath = min(sugarDaysToDeath, spiceDaysToDeath)
        return daysToDeath

    def findEmptyNeighborCells(self):
        emptyCells = []
        neighborCells = self.cell.neighbors
        for neighborCell in neighborCells:
            if neighborCell.agent == None:
                emptyCells.append(neighborCell)
        return emptyCells

    def findNearestHammingDistanceInDisease(self, disease):
        if self.immuneSystem == None:
            return 0
        diseaseTags = disease.tags
        diseaseLength = len(diseaseTags)
        bestHammingDistance = diseaseLength
        bestRange = [0, diseaseLength - 1]
        for i in range(len(self.immuneSystem) - diseaseLength):
            hammingDistance = 0
            for j in range(diseaseLength):
                if self.immuneSystem[i + j] != diseaseTags[j]:
                    hammingDistance += 1
            if hammingDistance < bestHammingDistance:
                bestHammingDistance = hammingDistance
                bestRange = [i, i + (diseaseLength - 1)]
        diseaseStats = {"distance": bestHammingDistance, "start": bestRange[0], "end": bestRange[1]}
        return diseaseStats

    def findHammingDistanceInTags(self, neighbor):
        if self.tags == None:
            return 0
        neighborTags = neighbor.tags
        hammingDistance = 0
        for i in range(len(self.tags)):
            if self.tags[i] != neighborTags[i]:
                hammingDistance += 1
        return hammingDistance

    def findMarginalRateOfSubstitution(self):
        spiceNeed = self.spice / self.spiceMetabolism if self.spiceMetabolism > 0 else 1
        sugarNeed = self.sugar / self.sugarMetabolism if self.sugarMetabolism > 0 else 1
        # Trade factor may increase amount of spice traded for sugar in a transaction
        self.marginalRateOfSubstitution = round(self.tradeFactor * (spiceNeed / sugarNeed), 2)

    def findRetaliatorsInVision(self):
        retaliators = {}
        for cell in self.cellsInVision:
            agent = cell["cell"].agent
            if agent != None:
                agentTribe = agent.tribe
                agentStrength = agent.wealth
                if agentTribe not in retaliators:
                    retaliators[agentTribe] = agentStrength
                elif retaliators[agentTribe] < agentStrength:
                    retaliators[agentTribe] = agentStrength
        return retaliators

    def findTribe(self):
        if self.tags == None:
            return None
        sugarscape = self.cell.environment.sugarscape
        numTribes = sugarscape.configuration["environmentMaxTribes"]
        zeroes = 0
        tribeCutoff = math.floor(len(self.tags) / numTribes)
        # Up to 11 tribes possible without significant color conflicts
        colors = ["green", "blue", "red", "orange", "purple", "teal", "pink", "mint", "blue2", "yellow", "salmon"]
        for tag in self.tags:
            if tag == 0:
                zeroes += 1
        self.tagZeroes = zeroes
        for i in range(1, numTribes + 1):
            if zeroes < (i * tribeCutoff) + 1 or i == numTribes:
                return colors[i - 1]
        # Default agent coloring
        return "red"

    def flipTag(self, position, value):
        self.tags[position] = value

    def gotoCell(self, cell):
        if(self.cell != None):
            self.resetCell()
        self.cell = cell
        self.cell.agent = self

    def isAlive(self):
        return self.alive

    def isCreditWorthy(self, sugarLoanAmount, spiceLoanAmount, loanDuration):
        if loanDuration == 0:
            return False
        sugarLoanCostPerTimestep = sugarLoanAmount / loanDuration
        spiceLoanCostPerTimestep = spiceLoanAmount / loanDuration
        sugarIncomePerTimestep = ((self.sugarMeanIncome - self.sugarMetabolism) - self.findCurrentSugarDebt()) - sugarLoanCostPerTimestep
        spiceIncomePerTimestep = ((self.spiceMeanIncome - self.spiceMetabolism) - self.findCurrentSpiceDebt()) - spiceLoanCostPerTimestep
        if sugarIncomePerTimestep >= 0 and spiceIncomePerTimestep >= 0:
            return True
        return False

    def isFertile(self):
        if self.sugar >= self.startingSugar and self.spice >= self.startingSpice and self.age >= self.fertilityAge and self.age < self.infertilityAge and self.fertilityFactor > 0:
            return True
        return False

    def isNeighborReproductionCompatible(self, neighbor):
        if neighbor == None:
            return False
        neighborSex = neighbor.sex
        neighborFertility = neighbor.isFertile()
        if self.sex == "female" and (neighborSex == "male" and neighborFertility == True):
            return True
        elif self.sex == "male" and (neighborSex == "female" and neighborFertility == True):
            return True
        else:
            return False

    def moveToBestCell(self):
        bestCell = self.findBestCell()
        if self.canReachCell(bestCell) == True:
            if self.aggressionFactor > 0:
                self.doCombat(bestCell)
            else:
                self.gotoCell(bestCell)
        return False
        

    def payDebt(self, loan):
        creditorID = loan["creditor"]
        creditor = self.socialNetwork[creditorID]["agent"]
        if creditor.isAlive() == False:
            if creditor.inheritancePolicy != "children":
                self.socialNetwork["creditors"].remove(loan)
                creditor.removeDebt(loan)
            else:
                self.payDebtToCreditorChildren(loan)
        elif self.sugar - loan["sugarLoan"] > 0 and self.spice - loan["spiceLoan"] > 0:
            self.sugar -= loan["sugarLoan"]
            self.spice -= loan["spiceLoan"]
            creditor.sugar = creditor.sugar + loan["sugarLoan"]
            creditor.spice = creditor.spice + loan["spiceLoan"]
            self.socialNetwork["creditors"].remove(loan)
            creditor.removeDebt(loan)
        else:
            sugarPayout = self.sugar / 2
            spicePayout = self.spice / 2
            sugarRepaymentLeft = loan["sugarLoan"] - sugarPayout
            spiceRepaymentLeft = loan["spiceLoan"] - spicePayout
            self.sugar -= sugarPayout
            self.spice -= spicePayout
            creditor.sugar = creditor.sugar + sugarPayout
            creditor.spice = creditor.spice + spicePayout
            creditorInterestRate = creditor.lendingFactor * creditor.baseInterestRate
            newSugarLoan = sugarRepaymentLeft + (creditorInterestRate * sugarRepaymentLeft)
            newSpiceLoan = spiceRepaymentLeft + (creditorInterestRate * spiceRepaymentLeft)
            self.socialNetwork["creditors"].remove(loan)
            creditor.removeDebt(loan)
            # Initiate new loan with interest compounded on previous loan and not transferring any new principal
            creditor.addLoanToAgent(self, self.lastMoved, 0, newSugarLoan, 0, newSpiceLoan, creditor.loanDuration)

    def payDebtToCreditorChildren(self, loan):
        creditorID = loan["creditor"]
        creditor = self.socialNetwork[creditorID]["agent"]
        creditorChildren = creditor.socialNetwork["children"]
        livingCreditorChildren = []
        for child in creditorChildren:
            if child.isAlive() == True:
                livingCreditorChildren.append(child)
        numLivingChildren = len(livingCreditorChildren)
        if numLivingChildren > 0:
            sugarRepayment = loan["sugarLoan"] / numLivingChildren
            spiceRepayment = loan["spiceLoan"] / numLivingChildren
            for child in livingCreditorChildren:
                child.addLoanToAgent(self, self.lastMoved, 0, sugarRepayment, 0, spiceRepayment, 1)
        self.socialNetwork["creditors"].remove(loan)
        creditor.removeDebt(loan)

    def removeDebt(self, loan):
        for debtor in self.socialNetwork["debtors"]:
            if debtor == loan:
                self.socialNetwork["debtors"].remove(debtor)
                return

    def resetCell(self):
        self.cell.resetAgent()
        self.cell = None

    def setFather(self, father):
        fatherID = father.ID
        if fatherID not in self.socialNetwork:
            self.addAgentToSocialNetwork(father)
        self.socialNetwork["father"] = father

    def setMother(self, mother):
        motherID = mother.ID
        if motherID not in self.socialNetwork:
            self.addAgentToSocialNetwork(mother)
        self.socialNetwork["mother"] = mother

    def spreadDisease(self, agent, disease):
        sugarscape = self.cell.environment.sugarscape
        sugarscape.addDisease(disease, agent)

    def updateDiseaseEffects(self, disease): 
        # If disease not in list of diseases, agent has recovered and undo its effects
        recoveryCheck = -1
        for diseaseRecord in self.diseases:
            if disease == diseaseRecord["disease"]:
                recoveryCheck = 1
                break

        sugarMetabolismPenalty = disease.sugarMetabolismPenalty * recoveryCheck
        spiceMetabolismPenalty = disease.spiceMetabolismPenalty * recoveryCheck
        visionPenalty = disease.visionPenalty * recoveryCheck
        movementPenalty = disease.movementPenalty * recoveryCheck
        fertilityPenalty = disease.fertilityPenalty * recoveryCheck
        aggressionPenalty = disease.aggressionPenalty * recoveryCheck

        self.sugarMetabolism = max(0, self.sugarMetabolism + sugarMetabolismPenalty)
        self.spiceMetabolism = max(0, self.spiceMetabolism + spiceMetabolismPenalty)
        self.vision = max(0, self.vision + visionPenalty)
        self.movement = max(0, self.movement + movementPenalty)
        self.fertilityFactor = max(0, self.fertilityFactor + fertilityPenalty)
        self.aggressionFactor = max(0, self.aggressionFactor + aggressionPenalty)

    def updateFriends(self, neighbor):
        neighborID = neighbor.ID
        neighborHammingDistance = self.findHammingDistanceInTags(neighbor)
        neighborEntry = {"friend": neighbor, "hammingDistance": neighborHammingDistance}
        if len(self.socialNetwork["friends"]) < self.maxFriends:
            self.socialNetwork["friends"].append(neighborEntry)
        else:
            maxHammingDistance = 0
            maxDifferenceFriend = None
            for friend in self.socialNetwork["friends"]:
                # If already a friend, update Hamming Distance
                if friend["friend"].ID == neighborID:
                    self.socialNetwork["friends"].remove(friend)
                    self.socialNetwork["friends"].append(neighborEntry)
                    return
                if friend["hammingDistance"] > maxHammingDistance:
                    maxDistanceFriend = friend
                    maxHammingDistance = friend["hammingDistance"]
            if maxHammingDistance > neighborHammingDistance:
                self.socialNetwork["friends"].remove(maxDistanceFriend)
                self.socialNetwork["friends"].append(neighborEntry)
        self.socialNetwork["bestFriend"] = self.findBestFriend()

    def updateLoans(self):
        for debtor in self.socialNetwork["debtors"]:
            debtorID = debtor["debtor"]
            debtorAgent = self.socialNetwork[debtorID]["agent"]
            # Cannot collect on debt since debtor is dead
            if debtorAgent.isAlive() == False:
                self.socialNetwork["debtors"].remove(debtor)
        for creditor in self.socialNetwork["creditors"]:
            timeRemaining = (self.lastMoved - creditor["loanOrigin"]) - creditor["loanDuration"]
            if timeRemaining == 0:
                self.payDebt(creditor)

    def updateMooreNeighbors(self):
        for direction, neighbor in self.vonNeumannNeighbors.items():
            self.mooreNeighbors[direction] = neighbor
        north = self.mooreNeighbors["north"]
        south = self.mooreNeighbors["south"]
        east = self.mooreNeighbors["east"]
        west = self.mooreNeighbors["west"]
        self.mooreNeighbors["northeast"] = north.cell.findEastNeighbor() if north != None else None
        self.mooreNeighbors["northeast"] = east.cell.findNorthNeighbor() if east != None and self.mooreNeighbors["northeast"] == None else None
        self.mooreNeighbors["northwest"] = north.cell.findWestNeighbor() if north != None else None
        self.mooreNeighbors["northwest"] = west.cell.findNorthNeighbor() if west != None and self.mooreNeighbors["northwest"] == None else None
        self.mooreNeighbors["southeast"] = south.cell.findEastNeighbor() if south != None else None
        self.mooreNeighbors["southeast"] = east.cell.findSouthNeighbor() if east != None and self.mooreNeighbors["southeast"] == None else None
        self.mooreNeighbors["southwest"] = south.cell.findWestNeighbor() if south != None else None
        self.mooreNeighbors["southwest"] = west.cell.findSouthNeighbor() if west != None and self.mooreNeighbors["southwest"] == None else None

    def updateMarginalRateOfSubstitutionForAgent(self, agent):
        agentID = agent.ID
        if agentID not in self.socialNetwork:
            self.addAgentToSocialNetwork(agent)
        self.socialNetwork[agentID]["marginalRateOfSubstitution"] = agent.marginalRateOfSubstitution

    def updateMeanIncome(self, sugarIncome, spiceIncome):
        # Define weight for moving average
        alpha = 0.05
        self.sugarMeanIncome = round((alpha * sugarIncome) + ((1 - alpha) * self.sugarMeanIncome), 2)
        self.spiceMeanIncome = round((alpha * spiceIncome) + ((1 - alpha) * self.spiceMeanIncome), 2)

    def updateNeighbors(self):
        self.updateVonNeumannNeighbors()
        self.updateMooreNeighbors()
        self.updateSocialNetwork()

    def updateSocialNetwork(self):
        for direction, neighbor in self.vonNeumannNeighbors.items():
            if neighbor == None:
                continue
            neighborID = neighbor.ID
            if neighborID in self.socialNetwork:
                self.updateTimesVisitedWithAgent(neighbor, self.lastMoved)
                self.updateMarginalRateOfSubstitutionForAgent(neighbor)
            else:
                self.addAgentToSocialNetwork(neighbor)
            self.updateFriends(neighbor)

    def updateTimesReproducedWithAgent(self, agent, timestep):
        agentID = agent.ID
        if agentID not in self.socialNetwork:
            self.addAgentToSocialNetwork(agent)
        self.socialNetwork[agentID]["timesReproduced"] += 1
        self.socialNetwork[agentID]["lastSeen"] = timestep

    def updateTimesTradedWithAgent(self, agent, timestep, transactions=0):
        agentID = agent.ID
        if agentID not in self.socialNetwork:
            self.addAgentToSocialNetwork(agent)
        self.socialNetwork[agentID]["timesTraded"] += transactions
        self.socialNetwork[agentID]["lastSeen"] = timestep

    def updateTimesVisitedWithAgent(self, agent, timestep):
        agentID = agent.ID
        if agentID not in self.socialNetwork:
            self.addAgentToSocialNetwork(agent)
        else:
            self.socialNetwork[agentID]["timesVisited"] += 1
            self.socialNetwork[agentID]["lastSeen"] = timestep

    def updateVonNeumannNeighbors(self):
        self.vonNeumannNeighbors["north"] = self.cell.findNorthNeighbor().agent
        self.vonNeumannNeighbors["south"] = self.cell.findSouthNeighbor().agent
        self.vonNeumannNeighbors["east"] = self.cell.findEastNeighbor().agent
        self.vonNeumannNeighbors["west"] = self.cell.findWestNeighbor().agent

    def __str__(self):
        return "{0}".format(self.ID)
