import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells.copy()
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        if cell in self.moves_made:
            raise NotImplementedError
        self.mark_safe(cell)
        self.moves_made.add(cell)
        
        #Get the cells around the inquiry cell
        #use .add() method to add to a set
        #The board goes from 0,0 to 7,7
        surrounding_cells = set()
        column = cell[0] - 1
        while True:
            if column == cell[0] + 2:
                break

            if column > -1 and column < 8:
                row = cell[1] - 1
                while True:
                    if row == cell[1] + 2:
                        break
                    if row > -1 and row < 8:
                        new_cell = (column,row)
                        surrounding_cells.add(new_cell)
                    row += 1

            column += 1
        if cell in surrounding_cells:
            surrounding_cells.remove(cell)
        
        new_sentence = Sentence(surrounding_cells,count)

        #After finding the surrounding cells, simplify the sentence
        for new_cell in surrounding_cells:
            if new_cell in self.safes:
                new_sentence.mark_safe(new_cell)
            elif new_cell in self.mines:
                new_sentence.mark_mine(new_cell)
        self.knowledge.append(new_sentence)

        #Refine the sentences we know
        refinement_index = 0
        while True:
            if refinement_index == 2:
                break

            #Clean up self.knowledge
            index = 0
            while True:
                if index == len(self.knowledge):
                    break
                if len(self.knowledge[index].cells) == 0:
                    del self.knowledge[index]
                else:
                    index += 1
            

            #Factor Sentences
            new_sentences = []
            remove_sentences = []
            index = 0

            #Compare every Sentence to every other sentence
            while True:
                if index == len(self.knowledge):
                    break

                sentence1 = self.knowledge[index]

                #Compare sentences
                for item in self.knowledge:
                    sentence2 = item

                    #Dont compare the same sentence to itself.
                    if sentence1 == sentence2:
                        continue
                    """
                    Infrence Rule 1:
                        If Sentence2 is a sub-set of Sentence1, You can turn Sentence1 into two sentences.

                    Infrence Rule 2:
                        Sentence1 is always the sentence with the higher count.
                        if sentence1.count - sentence2.count = len(unique_cells), than you can infer information.
                            Unique cells are cells of sentence1 not shared with sentence2.
                            Ex. ({A,B,D} = 2, {A,B,C} = 1) = ({A,B} = 1, {D} = 1, {C} = 0)
                        This infrence rule forces all of Sentence1's unique cells to be mines and all of Sentence2's Unique cells to be safe.
                        The shared cells become a new sentence with Sentence2.count mines.
                    
                    Infrence Rule 3:
                        If Sentence1 and Sentence2 have the same amount of cells, same amount of unique cells, same count,
                        and thier shared cells equal to thier count, than there are two possibilities:
                            A. The shared cells are mines and the unique cells are safe, or
                            B. The unique cells are mines and the shared cells may have mines or be safe.
                        You can use sentence1 and sentence2 to make a sentence3 with all shared and unique cells from the two
                        sentences, and calculate two diffrent counts for each scenario:
                            A. Sentence3 with a count equal to the number of shared cells, and
                            B. Sentence3 with a count equal to (len(unique_cells) + (count of mines - len(unique_cells))).
                        If you find a sentence in self.knowledge equal to either one of these variants of sentence3, then
                        you can infer information.
                    """

                    #Check for infrence rule 1
                    infrence1_applied = False
                    if len(sentence1.cells) > len(sentence2.cells):
                        appliable = True

                        #Confirm sentence2 is a subset of sentence1
                        for new_cell in sentence2.cells:
                            if new_cell not in sentence1.cells:
                                appliable = False
                                break

                        if appliable == True:
                            #Make the new sentence and save it
                            infrence1_applied = True
                            new_sentence = Sentence(sentence1.cells-sentence2.cells, sentence1.count - sentence2.count)
                            new_sentences.append(new_sentence)
                            remove_sentences.append(sentence1)

                    #Check for infrence rule 2
                    infrence2_applied = False
                    if infrence1_applied == False:
                        shared_cells = set()
                        unique_cells = set()
                        for new_cell in sentence1.cells:
                            if new_cell in sentence2.cells:
                                shared_cells.add(new_cell)
                            else:
                                unique_cells.add(new_cell)
                        if len(shared_cells) > 1 and sentence1.count - sentence2.count == len(unique_cells):
                            infrence2_applied = True
                            #Mark the known mines
                            for mine in unique_cells:
                                self.mark_mine(mine)

                            #Mark the known safes
                            safes = set()
                            for safe in sentence2.cells:
                                if safe not in shared_cells:
                                    safes.add(safe)

                            for safe in safes:
                                self.mark_safe(safe)

                            #Make new senteces and mark the old ones for removal
                            new_sentence = Sentence(shared_cells, sentence2.count)
                            new_sentences.append(new_sentence)
                            remove_sentences.append(sentence1)
                            remove_sentences.append(sentence2)
                
                    #Check for infrence method 3
                    if infrence1_applied == False and infrence2_applied == False:
                        if sentence1.count == sentence2.count and len(sentence1.cells) == len(sentence2.cells):

                            shared_cells = set()
                            sentence1_unique_cells = set()

                            for item in sentence1.cells:
                                if item in sentence2.cells:
                                    shared_cells.add(item)
                                else:
                                    sentence1_unique_cells.add(item)
                            if len(shared_cells) == sentence1.count:

                                sentence2_unique_cells = set()
                                for item in sentence2.cells:
                                    if item not in shared_cells:
                                        sentence2_unique_cells.add(item)
                                
                                #Search for the two possible sentences.
                                possibility_cells = shared_cells| sentence1_unique_cells | sentence2_unique_cells
                                possibility_1 = Sentence(possibility_cells, len(shared_cells))
                                possibility_2 = Sentence(possibility_cells, len(sentence1_unique_cells) + sentence1.count)

                                if possibility_1 in self.knowledge:
                                    """
                                    print("Used infrence method 3")
                                    print("Sentence1: ", sentence1.cells, sentence1.count)
                                    print("Sentence2: ", sentence2.cells, sentence2.count)
                                    print("Mines: ", shared_cells)
                                    print("Safes: ", sentence1_unique_cells|sentence2_unique_cells)
                                    """
                                    for item in shared_cells:
                                        self.mark_mine(item)
                                    for item in sentence1_unique_cells|sentence2_unique_cells:
                                        self.mark_safe(item)

                                elif possibility_2 in self.knowledge:
                                    """
                                    print("Used infrence method 3")
                                    print("Sentence1: ", sentence1.cells, sentence1.count)
                                    print("Sentence2: ", sentence2.cells, sentence2.count)
                                    print("Mines: ", sentence1_unique_cells|sentence2_unique_cells)
                                    print("Unknown: ", shared_cells)
                                    """
                                    for item in sentence1_unique_cells|sentence2_unique_cells:
                                        self.mark_mine(item)
                                    new_sentences.append(Sentence(shared_cells, sentence1.count - len(sentence1_unique_cells)))
                                else:
                                    pass



                index += 1

            #Remove old sentences
            knowledge_index = 0
            while True:
                if knowledge_index == len(self.knowledge):
                    break
                if self.knowledge[knowledge_index] in remove_sentences:
                    del self.knowledge[knowledge_index]
                else:
                    knowledge_index += 1

            #Add new sentences
            for item in new_sentences:
                self.knowledge.append(item)





            #After searching the inquiry square search for new mines and safes
            for item in self.knowledge:
                new_safes = item.known_safes()
                new_mines = item.known_mines()
                for safe_cell in new_safes:
                    if safe_cell not in self.safes:
                        self.mark_safe(safe_cell)
                        self.safes.add(safe_cell)

                for mine_cell in new_mines:
                    if mine_cell not in self.mines:
                        self.mark_mine(mine_cell)
                        self.mines.add(mine_cell)
        
            refinement_index += 1
        
        for items in self.knowledge:
            print(items.cells)
        
        


        




    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe in self.safes:
            if safe not in self.moves_made:
                return safe
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_moves = []
        row = 0
        while True:
            if row == 8:
                if len(possible_moves) < 9:
                    return None
                while True:
                    random_move = random.choice(possible_moves)
                    if random_move not in self.mines:
                        return random_move
            
            column = 0
            while True:
                if column == 8:
                    break

                if (row, column) not in self.moves_made:
                    possible_moves.append((row, column))
                
                column += 1
            row += 1

