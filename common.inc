// Number of slaves.
#const NUM_SLAVES#
const int NUM_SLAVES = #NUM_SLAVES#;
// Number of slaves whose failure can be tolerated.
const int REDUNDANT_SLAVES = 1;
// Minimum required number of slaves for the system to function.
const int MIN_SLAVES = NUM_SLAVES - REDUNDANT_SLAVES;

// Unit of time is seconds.
//////////////////////////
const double SEC_PER_MILLISEC = 1/1000;
const int SEC_PER_MINUTE = 60;
const int SEC_PER_HOUR = 60 * SEC_PER_MINUTE;
const int SEC_PER_DAY = 24 * SEC_PER_HOUR;
const int SEC_PER_MONTH = 30 * SEC_PER_DAY;


const double e = 2.71828;

// Megabits per second speed of the Ethernet links.
const int mbps = 100;
// Bits per second speed of the Ethernet links.
const int bps = mbps * pow(10, 6);

// Number of TMs transmitted per EC.
const int tms_per_ec = 3;
// Frame size for TMs.
const int tm_size_bytes = 64;
const int tm_size_bits = tm_size_bytes * 8;
// Time to transmit a single TM.
const double tm_duration = tm_size_bits / bps;

// EC duration
const double ec_duration = 1 * SEC_PER_MILLISEC;
// EC rate
const double ec_r = 1/ec_duration;

// Exponent for bit error ratio.
const double bit_error_ratio_exponent;
// Bit error ratio: 1 bit lost out of 10^bit_error_ratio_exponent,
// e.g., if bit_error_ratio_exponent = 6, then 1 bit is lost out of 10^6 =
// 1,000,000 bits.
const double bit_error_ratio = 1/pow(10, bit_error_ratio_exponent);
// Bit error rate.
const double bit_error_r = bit_error_ratio * bps;
// EC corruption probability.
// We assume bit errors are arrivals of a Poisson process. An EC corruption
// occurs when all TMs of an EC are corrupted, i.e., when all TMs are affected
// by at least 1 bit error. Note that since we use a Poisson process model, all
// that matters for the EC corruption probability is the bit error rate, the TM
// duration, and the number of TMs.
const double ec_corruption_p =
    pow(1 - pow(e, -bit_error_r * tm_duration), tms_per_ec);

// Rate with which all TMs of a single EC are lost on a single link.
const double ec_corruption_r = ec_r * ec_corruption_p;
