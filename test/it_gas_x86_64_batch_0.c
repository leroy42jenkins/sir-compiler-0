#include <stdio.h>
#include <stdint.h>

extern int64_t add_2_ints(int64_t a, int64_t b);

void run_add_2_ints() {
	int64_t a = 1;
	int64_t b = 2;
    int64_t c = add_2_ints(a, b);
	printf("test 1:\n");
	printf("\t%lld + %lld = %lld\n", a, b, c);
}

extern int64_t simple_inc(int64_t a);
extern int64_t simple_inc_test(int64_t a);

void run_simple_inc_test() {
	int64_t a = 1;
    int64_t b = simple_inc_test(a);
	printf("test 2:\n");
	printf("\t%lld + 1 = %lld\n", a, b);
}

extern int64_t sum_lots_of_args(int64_t a, int64_t b, int64_t c,
	int64_t d, int64_t e, int64_t f, int64_t g, int64_t h);

void run_sum_lots_of_args() {
	int64_t s = sum_lots_of_args(1LL, 2LL, 3LL, 4LL,
		5LL, 6LL, 7LL, 8LL);
	printf("test 3:\n");
	printf("\t1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 = %lld\n", s);
}

extern int64_t swap_chars(char *a, char *b);

void run_swap_chars() {
	char a = 'a';
	char b = 'b';
	printf("test 4:\n");
	printf("\toriginal: %c %c\n", a, b);
	int64_t r = swap_chars(&a, &b);
	printf("\tswapped: %c %c\n", a, b);
}

extern int64_t reverse_char_array(char *begin, char *end);

void run_reverse_char_array() {
	char ar[6] = { 'a', 'b', 'c', 'd', 'e', '\0' };
	printf("test 5:\n");
	printf("\toriginal: %s\n", ar);
	int64_t r = reverse_char_array(ar, ar + 4);
	printf("\treversed: %s\n", ar);
}

extern int64_t sum_internal_ar(int64_t blank);

void run_sum_internal_ar() {
	int64_t s = sum_internal_ar(0LL);
	printf("test 6:\n");
	printf("\t1 + 2 + 3 = %lld\n", s);
}

int main(int argc, char **argv) {
	run_add_2_ints();
	run_simple_inc_test();
	run_sum_lots_of_args();
	run_swap_chars();
	run_reverse_char_array();
	run_sum_internal_ar();
	return 0;
}
