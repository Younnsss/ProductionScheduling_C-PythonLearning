#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "time.h"
//Maybe not all include are usefull
//gcc -shared -o main.dll -fPIC sort.c

typedef enum {
    m_true,
    m_false
} m_bool;


void johnson(int *m1,int *m2,int *p, int size){

    //contains the times for the first machine and M2_copy for the second. We will order the indexes in p
    int minimum, min_index, index_beginning, index_end;
    index_beginning = 0;
    index_end = size -1;//These are the indexes we are going to use to append the number of the jobs in p
    m_bool min_in_m1_copy;
    int *m1_copy;
    int *m2_copy;
    m1_copy = (int *) malloc(size*sizeof(int));
    m2_copy = (int *) malloc(size*sizeof(int));
    for (int i = 0; i < size; ++i) {
        m1_copy[i] = m1[i];
        m2_copy[i] = m2[i];//copying because we will modify the array
    }
    for (int i = 0; i < size; ++i) {//We have to do that for every job
        min_index = 0;
        min_in_m1_copy = m_true;
        minimum = 100000;
        for (int j = 0; j < size; ++j) {//finding the minimum
            if (m1_copy[j] < minimum) {
                minimum = m1_copy[j];
                min_index = j;
                min_in_m1_copy = m_true;
            }
            if (m2_copy[j] < minimum) {
                minimum = m2_copy[j];
                min_index = j;
                min_in_m1_copy = m_false;
            }
        }

        if(min_in_m1_copy == m_true) {
            p[index_beginning] = min_index;
            m1_copy[min_index] = 100000;
            m2_copy[min_index] = 100000;//We put -1 to indicate that the cell doesn't count anymore
            index_beginning++;
        }
        else{
            p[index_end] = min_index;
            m1_copy[min_index] = 100000;
            m2_copy[min_index] = 100000;//We put -1 to indicate that the cell doesn't count anymore
            index_end--;
        }
    }
}

m_bool fit_before_pause(int *tab, int *m1, int size, int pause_start){
    /*
    Checking if a task can fit before the pause
    */
    m_bool fits = m_true;
    int total_time = 0;
    for (int i = 0; i < size; i++)
    {
        total_time += m1[tab[i]];//Computing the total time on m1
    }
    if(total_time > pause_start){
        fits = m_false;
    }
    return fits;
}

int duration(int *m1,int *m2,int *p, int size, int start_time, int duration){
    /*
    returns the duration of a certain order
    */
    int current_time_m1 = 0;
    int current_time_m2 = 0;
    m_bool increment_pause = m_false;
    for (int i = 0; i < size; i++)
    {
        if(current_time_m1 + m1[p[i]] <= start_time){
            current_time_m1 += m1[p[i]];
        }
        else if(increment_pause == m_false && current_time_m1 + m1[p[i]] > start_time){
            increment_pause = m_true;
            current_time_m1 = start_time + duration + m1[p[i]];
        }
        else if(increment_pause == m_true){
            current_time_m1 += m1[p[i]];
        }
        if(current_time_m2 > current_time_m1){
            current_time_m2 += m2[p[i]];
        }
        else{
            current_time_m2 = current_time_m1 + m2[p[i]];
        }
        //printf(" i = %d; time m1 %d ; time m2 %d\n", i, current_time_m1, current_time_m2);

    }
    //the maximum time will be the one on m2
    return current_time_m2;
}

void copy_tab(int *tab_1, int *tab_2, int size){
    /*
    We copy tab_1 to tab_2
    */
   for (int i = 0; i < size; i++)
   {
       tab_2[i] = tab_1[i];
   }   
}

int * pop_tab(int *tab, int index, int size){
    int *n_tab;
    n_tab = (int*) malloc((size-1)*sizeof(int));
    for (int i = 0; i < index; i++)
    {
        n_tab[i] = tab[i];
    }
    
    for (int i = index; i < size-1; i++)
    {
        n_tab[i] = tab[i+1];
    }
    return n_tab;
}

void join_tab(int *tab_1, int size_1, int *tab_2, int size_2, int *p){
    /*
    We will "add" tab_1 + tab_2 in p
    */
   for (int i = 0; i < size_1; i++)
   {
       p[i] = tab_1[i];
   }
   for (int i = size_1; i < size_1 + size_2; i++)
   {
       p[i] = tab_2[i-size_1];
   }
   
}

void swap_values(int *tab_1, int index_1, int *tab_2, int index_2){
    /*
    We will swap tab_1[index_1] and tab_2[index_2]
    */
   int prov = tab_1[index_1];
   tab_1[index_1] = tab_2[index_2];
   tab_2[index_2] = prov;
}

int * append_tab(int *tab, int size, int value){
    if(size == 0){
        tab = (int*) malloc(sizeof(int));
    }
    else{
        tab = realloc(tab, (size+1)*sizeof(int));
    }
    tab[size] = value;
    return tab;
}

void print_tab(int *tab, int size){
    /*
    Prints all the values of an array
    */
   for (int i = 0; i < size; i++)
   {
       printf("%d - ", tab[i]);
   }
   printf("\n");
}

void final_johnson(int *m1,int *m2, int *p, int size, int pause_start, int pause_duration){
    /*
    Same as johnson but we put indexmiddle and duration at the end of the tab
    */
    int *tab_johnson;
    tab_johnson = (int*) malloc(size * sizeof(int));//provisory array to store the results of johnson algorithm
    johnson(m1, m2, tab_johnson, size);
    int total_duration = duration(m1, m2, tab_johnson, size, pause_start, pause_duration);
    int current_time_m1 = 0;
    int index_middle = size;//By default, pause is after all the jobs
    for (int i = 0; i < size; i++)
    {
        current_time_m1 += m1[tab_johnson[i]];
        if(current_time_m1 > pause_start){
            index_middle = i;
            break;
        }
    }
    copy_tab(tab_johnson, p, size);
    p[size] = index_middle;
    p[size+1] = total_duration;
}

void final_sort(int *m1,int *m2, int *p, int size, int pause_start, int pause_duration, int precision){
    //We will modify the array p. The size will be size + 1 because the last element will store index_middle
    //printf("pause start %d, pause duration %d, precision %d\n", pause_start, pause_duration, precision);
    int *tab_johnson;
    tab_johnson = (int*) malloc(size * sizeof(int));//provisory array to store the results of johnson algorithm
    johnson(m1, m2, tab_johnson, size);
    //We initialize the duration with the results given by johnson
    int total_duration = duration(m1, m2, tab_johnson, size, pause_start, pause_duration);
    printf("Start duration is : %d\n", total_duration);
    print_tab(tab_johnson, size);
    int current_time_m1 = 0;
    int index_middle = size;//By default, pause is after all the jobs
    for (int i = 0; i < size; i++)
    {
        current_time_m1 += m1[tab_johnson[i]];
        if(current_time_m1 > pause_start){
            index_middle = i;
            printf("INDEX middle is %d\n", index_middle);
            break;
        }
    }
    //Splitting the tab 
    int *tab_before;
    int *tab_after;
    int size_before = index_middle;
    int size_after = size-index_middle;
    tab_before = (int*)malloc(size_before*sizeof(int));
    tab_after = (int*)malloc(size_after*sizeof(int));
    for (int i = 0; i < index_middle; i++)
    {
        tab_before[i] = tab_johnson[i];
    }
    for (int i = index_middle; i < size; i++)
    {
        tab_after[i- index_middle] = tab_johnson[i];
    }
    int *tab_before_prov;//We will try to modificate in these tabs and copy in the others if it works
    int *tab_after_prov;
    tab_before_prov = (int*)malloc(size_before*sizeof(int));
    tab_after_prov = (int*)malloc(size_after*sizeof(int));
    copy_tab(tab_before, tab_before_prov, size_before);
    copy_tab(tab_after, tab_after_prov, size_after);
    int *tab_to_join;
    tab_to_join = (int*) malloc(size*sizeof(int));//In this tab, we will join before and after
    int cpt_unsuccessfull = 0;//We count the number of successive useless actions (actions that increase the time)
    if(size_after == 0 || size_before == 0){
        cpt_unsuccessfull = size * precision + 1;//Impossible to swap, we set cpt_uncessfull to a high value so we don't get stuck in the while
    }
    /*
    We will try to swap values after and before
    We stop when we reach n unsuccesfull swap (number is size * precision)
    */
    int d;
    while (cpt_unsuccessfull < size*precision)
    {
        for (int i = size_before-1; i >= 0; i--)//Looping before
        {
            for (int j = 0; j < size_after; j++)//looping after
            {
                swap_values(tab_before_prov, i, tab_after_prov, j);//We swap on provisory array
                if(fit_before_pause(tab_before_prov, m1, size_before, pause_start) == m_true){//We check if the swap can be done before checking duration
                    join_tab(tab_before_prov, size_before, tab_after_prov, size_after, tab_to_join);
                    d = duration(m1, m2, tab_to_join, size, pause_start, pause_duration);
                    if(d < total_duration){
                        total_duration = d;//We set the new minimum
                        printf("SWAPPING\n");
                        swap_values(tab_before, i, tab_after, j);//We do that to avoid a full copy
                        cpt_unsuccessfull = 0;//We reset since we did a successful swap
                    }
                    else{
                        cpt_unsuccessfull ++;
                        swap_values(tab_before_prov, i, tab_after_prov, j);//We swap again to avoid copying
                    }

                }
                else{
                    cpt_unsuccessfull ++;
                    swap_values(tab_before_prov, i, tab_after_prov, j);//We swap again to avoid copying
                }
            }
            if(cpt_unsuccessfull >= size*precision){
                break;
            }
        }
    }
    
    //Now we try to insert elements into the before part
    //We don't change tab_before and tab_after so that the indexes don't change
    int a = size_after;//We copy since size after is going to change
    tab_after = NULL;//We empty our tab, we will add elements to it if they don't fit
    int cpt = 0;
    for (int i = 0; i < a; i++)
    {
        tab_before_prov = realloc(tab_before_prov, (size_before+1)*sizeof(int));
        tab_before_prov[size_before] = tab_after_prov[i];//appending at the end
        if(fit_before_pause(tab_before_prov, m1, size_before + 1, pause_start) == m_true){
            size_before ++;
        }
        else{
            tab_before_prov = realloc(tab_before_prov, size_before*sizeof(int));//We remove the last element
            tab_after = append_tab(tab_after, cpt, tab_after_prov[i]);//We add the task that doesn't fit to our empty array
            cpt++;
        }
    }

    size_after = cpt;
    join_tab(tab_before_prov, size_before, tab_after, size_after, tab_to_join);

    total_duration = duration(m1, m2, tab_to_join, size, pause_start, pause_duration);

    printf("End duration is : %d\n", total_duration);
    print_tab(tab_before_prov, size_before);
    print_tab(tab_after, size_after);
    copy_tab(tab_to_join, p, size);
    p[size] = size_before;
    p[size+1] = total_duration;
}

int main(){
    
}