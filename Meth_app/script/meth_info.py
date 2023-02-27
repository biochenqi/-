import sys,os

prefix=sys.argv[1]
file_cov='%s_R1.picard.cov.txt'%prefix
file_cov_dedup='%s_R1_dedup.picard.cov.txt'%prefix
file_bismark = '%s_R1.clean_bismark_bt2_PE_report.txt'%prefix
file_coverage = '%s.coverage'%prefix

with open(file_cov,'r') as f:
    check = 0
    for line in f:
        if line.startswith('BAIT_SET'):
            head_name = line.strip().split('\t')
            check = 1
            continue
        if check:
            line = line.strip().split('\t')
            total_read = int(int(line[5])/2)
            capture_rate = line[17]
            check =0 

with open(file_cov_dedup,'r') as f:
    check = 0
    for line in f:
        if line.startswith('BAIT_SET'):
            head_name = line.strip().split('\t')
            check = 1
            continue
        if check:
            line = line.strip().split('\t')
            total_read_dedup = int(int(line[5])/2)
            capture_rate_dedup = line[17]
            pct_2x= line[head_name.index('PCT_TARGET_BASES_2X')]
            pct_10x= line[head_name.index('PCT_TARGET_BASES_10X')]
            pct_50x = line[head_name.index('PCT_TARGET_BASES_50X')]
            pct_100x = line[head_name.index('PCT_TARGET_BASES_100X')]
            check =0 

with open(file_bismark,'r') as f:
    for line in f:
        if ':' in line:
            num_info = line.strip().split(':')[1].strip()
        if line.startswith('C methylated in CpG context:'):
            mC_CpG = num_info
        elif line.startswith('C methylated in CHG context:'):
            mC_CHG = num_info
        elif line.startswith('C methylated in CHH context:'):
            mC_CHH = num_info
        elif line.startswith('Sequence pairs did not map uniquely:'):
            ReadsHit = num_info
        elif line.startswith('Number of paired-end alignments with a unique best hit:'):
            UniqHit = num_info
            
    ReadsHit  = int(ReadsHit) + int(UniqHit)

with open(file_coverage,'r') as f:
    total_count,count_1,min_num,count_500,average = 0,0,10000000,0,0
    for line in f:
        if line.startswith('chrom'):
            check = 1
            continue
        elif line.startswith('Locus'):
            check = 0
            continue

        line = line.strip().split("\t") if check else line.strip().split(',')
        cov_dep = float(line[-2]) if check else float(line[-1])
        total_count += 1
        average += cov_dep
        min_num = cov_dep if cov_dep < min_num else min_num

        if cov_dep>=1:
            count_1 += 1
        if cov_dep >= 500:
            count_500 += 1
    average = average/total_count
    count_1 = count_1/total_count
    count_500 = count_500/total_count

def stat_info(prefix,suffix):
    fastq_stat3 = '/project/Analysis/MethyScirpt/fastq_stat3'
    info = os.popen('%s %s_%s'%(fastq_stat3,prefix,suffix))
    info = info.read()
    info = [float(i) for i in info.strip().split('\t')]
    return info

read_1 = stat_info(prefix,'combined_R1.fastq.gz')
read_2 = stat_info(prefix,'combined_R2.fastq.gz')
read = [read_1[i] + read_2[i] for i in range(len(read_1))]

read_1_dedup = stat_info(prefix,'R1.clean.fastq.gz')
read_2_dedup = stat_info(prefix,'R2.clean.fastq.gz')
read_dedup = [read_1_dedup[i] + read_2_dedup[i] for i in range(len(read_1))]

name = prefix.split('-')
# print('样本编号\tSampleName\tReads_b\tQ30_b\tReads_f\tQ30_f\tReadsHit\tUniqHit\tmC_CpG\tmC_CHG\tmC_CHH\tTOTAL_MAPREADS_A\tPCT_SELECTED_BASES_A\tTOTAL_MAPREADS_U\tPCT_SELECTED_BASES_U\tbase\taverage\tmin\t1x\t10x\t100x\t500x')
print('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%.2f\t%s\t%s\t%s\t%s\t%s'%('-'.join(name[:-2]), '-'.join(name[-2:]), int(int(read[0])/2), read[7]/2, int(int(read_dedup[0])/2), read_dedup[7]/2, ReadsHit, UniqHit, mC_CpG, mC_CHG, mC_CHH, total_read, capture_rate, total_read_dedup, capture_rate_dedup, total_count, average, int(min_num), count_1,pct_10x,pct_100x,count_500))