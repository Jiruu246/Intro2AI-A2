#my_list = ['a', 'b', 'c']

def my_funct():
    my_list = ['a', 'b', 'c']
    my_list.append('c')
    def my_funct2(list):
        list.append('e')
    
    def my_funct3(list):
        list.append('f')
        
    my_funct2(my_list)
    my_funct3(my_list)
    
    print(my_list)
    
my_funct()
