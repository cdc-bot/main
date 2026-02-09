def filter_to_numbers(string:str):
    ret = ""
    for char in string:
        if char in "1234567890.":
            ret = ret + char
    if ret != "":
        return ret
    else:
        return "0"
class NumberAbbreviations:
    abbreviations = {}
    def add_abbreviation(self,symbol,power_of_ten):
        self.abbreviations[symbol] = pow(10,power_of_ten)
    def abbrevate(self,n):
        absolute = abs(n)
        for abbreviation in self.abbreviations:
            if absolute > self.abbreviations[abbreviation]: 
                return f"{round(n/self.abbreviations[abbreviation],2)}{abbreviation}"
        return n
    def unpack(self,n_str:str):
        for abbreviation in self.abbreviations:
            abr = self.abbreviations[abbreviation]
            if n_str.lower().endswith(abbreviation.lower()):
                new = filter_to_numbers(n_str)
                return float(new)*abr
        return float(filter_to_numbers(n_str))
    
number_abbreviation = NumberAbbreviations()
number_abbreviation.add_abbreviation("K",3)
number_abbreviation.add_abbreviation("M",6)
number_abbreviation.add_abbreviation("B",9)
number_abbreviation.add_abbreviation("T",12)
number_abbreviation.add_abbreviation("QUAD",15)
number_abbreviation.add_abbreviation("QUINT",18)
number_abbreviation.add_abbreviation("SEX",21)
number_abbreviation.add_abbreviation("SEP",24)
number_abbreviation.add_abbreviation("OCT",27)
number_abbreviation.add_abbreviation("NON",30)
number_abbreviation.add_abbreviation("DEC",33)
number_abbreviation.add_abbreviation("VIG",63)
number_abbreviation.add_abbreviation("GOOG",100)
number_abbreviation.add_abbreviation("CENT",303)
#number_abbreviation.add_abbreviation("GPLEX",pow(10,100))
