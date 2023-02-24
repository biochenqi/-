#!/bin/bash
# **********************************************************
# * Author        : chenqi
# * Email         : chenqi@gooalgene.com
# * Create time   : 2021-10-13 14:23
# * Last modified : 2021-10-13 14:23
# * Filename      : meth.sh
# * Description   : 
# **********************************************************
########################help############
helpdoc(){
    cat <<EOF
Description:
    this script is made for 
    running mNGS Ananysis

Usage:
    $0 --R1 <R1.fq.gz> [--R2 <R2.fq.gz>] --work_dir <dir> -t <int> [--AdapterEnd...]

Option:
    --R1 <fq>    input R1 file (注意：需要严格按照R1 R2的输入顺序当为双链输入数据时)
    --R2 <fq>    input R2 file （注意：需要严格按照R1 R2的输入顺序当为双链输入数据时）
    --work_dir <dir>      work dir[default: . ]
    -t|--thread <int>     set thread of the process [3]
    --AdapterEnd    set Sequence of an adapter ligated to the 3' end (paired data: of the first read). [AGATCGGAAGAGCACACGTC]
    --AdapterTop    set Sequence of an adapter ligated to the 5' end (paired data: of the first read). [ACACGACGCTCTTCCGATCT]
    --TrimmomaticAdapterMismatch    
    --TrimmomaticPalindromeThreshold    
    --TrimmomaticSimpleThreshold    
    --TrimmomaticMinAdapterLength       Require MINLENGTH overlap between read and adapter for an adapter to be found. [5]
    --TrimmomaticWindowSize 
    --TrimmomaticRequiredQuality    
    --TrimmomaticStartQuality   
    --TrimmomaticEndQuality 
    --TrimmomaticMinLength      Discard reads shorter than LEN.[40]
    --TrimmomaticAverageQuality     Trim low-quality bases from 5' and/or 3' ends of each read before adapter removal. [20]

EOF
}
if [ $# = 0 ];then
    helpdoc
    exit 1
fi
# TEMP=`getopt -o ht: --long help,input_reads:,work_dir:,thread:,prefix: -n 'bash' -- "$@"`
TEMP=`getopt -o ht: --long help,R1:,R2:,work_dir:,thread:,AdapterEnd:,AdapterTop:,TrimmomaticAdapterMismatch:,TrimmomaticPalindromeThreshold:,TrimmomaticSimpleThreshold:,TrimmomaticMinAdapterLength:,TrimmomaticWindowSize:,TrimmomaticRequiredQuality:,TrimmomaticStartQuality:,TrimmomaticEndQuality:,TrimmomaticMinLength:,TrimmomaticAverageQuality: -n 'bash' -- "$@"`
if [ $? != 0 ]; then echo "Terminating...." >&2 ;exit 1; fi
eval set -- "$TEMP"

#参数设置
input_r1_reads=
input_r2_reads=
work_dir="."
thread=3
AdapterEnd='AGATCGGAAGAGCACACGTC'
AdapterTop='ACACGACGCTCTTCCGATCT'
TrimmomaticAdapterMismatch='2'
TrimmomaticPalindromeThreshold='30'
TrimmomaticSimpleThreshold='10'
TrimmomaticMinAdapterLength='5'
TrimmomaticWindowSize='5'
TrimmomaticRequiredQuality='15'
TrimmomaticStartQuality='15'
TrimmomaticEndQuality='15'
TrimmomaticMinLength='40'
TrimmomaticAverageQuality='20'
while true;do
    case "$1" in
        -h|--help)
                helpdoc
                exit 1;;
        --R1) input_r1_reads="$2";shift 2;;
        --R2) input_r2_reads="$2";shift 2;;
        --work_dir) work_dir="$2";shift 2;;
        -t|--thread) thread="$2";shift 2;;
        --AdapterEnd) AdapterEnd="$2";shift 2;;
        --AdapterTop) AdapterTop="$2";shift 2;;
        --TrimmomaticAdapterMismatch) TrimmomaticAdapterMismatch="$2";shift 2;;
        --TrimmomaticPalindromeThreshold) TrimmomaticPalindromeThreshold="$2";shift 2;;
        --TrimmomaticSimpleThreshold) TrimmomaticSimpleThreshold="$2";shift 2;;
        --TrimmomaticMinAdapterLength) TrimmomaticMinAdapterLength="$2";shift 2;;
        --TrimmomaticWindowSize) TrimmomaticWindowSize="$2";shift 2;;
        --TrimmomaticRequiredQuality) TrimmomaticRequiredQuality="$2";shift 2;;
        --TrimmomaticStartQuality) TrimmomaticStartQuality="$2";shift 2;;
        --TrimmomaticEndQuality) TrimmomaticEndQuality="$2";shift 2;;
        --TrimmomaticMinLength) TrimmomaticMinLength="$2";shift 2;;
        --TrimmomaticAverageQuality) TrimmomaticAverageQuality="$2";shift 2;;
        --)shift ; break;;
        *)echo "Internal error!";exit 1;;
    esac
done

#judge if the dir exists
if [ ! -d "$work_dir" ];then
    mkdir $work_dir
fi
cd $work_dir
#judge if input fastq file
if [ ! -n "$input_r1_reads" ];then
    echo "fastq file must be given!"
    exit 1
fi
if [ ! -f "$input_r1_reads" ];then
    echo "$input_reads does not exists,please check it!"
    exit 1
fi

#软件路径
AddGroups='/project/NIPT/NIPT_Analysis/biosoft/picard/picard-tools-1.117/AddOrReplaceReadGroups.jar'
cutadapt='/usr/local/bin/cutadapt'
bismark='/home/chenqi/bin/soft/bismark'
samtools='/usr/bin/samtools'
sambamba='/biostack/tools/protocols/novo-seq-0.0.1/binaries/sambamba'
AddGroups='/project/NIPT/NIPT_Analysis/biosoft/picard/picard-tools-1.117/AddOrReplaceReadGroups.jar'
Bisextractor='/project/usr/chenqi/software/Bismark/bismark_methylation_extractor'
GATKSoftwar='/biostack/tools/variation/GenomeAnalysisTK-3.8.1/GenomeAnalysisTK.jar'
CalculateHsMetrics='/project/NIPT/NIPT_Analysis/biosoft/picard/picard-tools-1.117/CalculateHsMetrics.jar'
gatk='/home/chenqi/bin/soft/gatk'
#文件或文件夹路径
script_path='/project/usr/chenqi/test/test_read/Meth_app/script'
ref_fasta='/project/NIPT/database/hg19.fa'
BisRef_path='/project/NIPT/database/'
bed_file='/project/usr/chenqi/test/test_cancer_methlation_deal/true_urinary_data/bin/all_target_segments_covered_by_probes_Methylation_Sansure_MedStrin_V2_TE-99014536_hg19_210521025021.bed'
interval_file='/project/usr/chenqi/test/test_cancer_methlation_deal/true_urinary_data/bin/urinary.intervals'

sampleID=`python3 -c "import sys;print(sys.argv[1].split('/')[-1].split('_')[0])" $input_r1_reads`
echo $sampleID start at time `date +%F'  '%H:%M:%S`
if [ ! -d $sampleID ];then
    mkdir $sampleID
fi
cd $sampleID
ln -s $input_r1_reads .
ln -s $input_r2_reads .
#去接头
echo '#######################Trimmomati########################'
$cutadapt -j $thread -q $TrimmomaticAverageQuality -O $TrimmomaticMinAdapterLength -m $TrimmomaticMinLength -a $AdapterEnd -A AGATCGGAAGAGCGTCGTGT $input_r1_reads $input_r2_reads -o ${sampleID}_R1.cutadapt.fastq.gz -p ${sampleID}_R2.cutadapt.fastq.gz > cutadapt.log
$cutadapt -j $thread -q $TrimmomaticAverageQuality -O $TrimmomaticMinAdapterLength -m $TrimmomaticMinLength -g $AdapterTop -G GACGTGTGCTCTTCCGATCT ${sampleID}_R1.cutadapt.fastq.gz ${sampleID}_R2.cutadapt.fastq.gz -o ${sampleID}_R1.clean.fastq.gz -p ${sampleID}_R2.clean.fastq.gz >> cutadapt.log
rm ${sampleID}_R1.cutadapt.fastq.gz ${sampleID}_R2.cutadapt.fastq.gz

#序列比对
echo '#########################bismark#########################'
echo '#########################bismark#########################' >> cmd.log
echo $bismark -p $thread --ambiguous --unmapped --score_min L,0,-0.2 --temp_dir temp/ --bowtie2 $BisRef_path -o . -1 ${sampleID}_R1.clean.fastq.gz -2 ${sampleID}_R2.clean.fastq.gz >cmd.log
$bismark -p $thread --ambiguous --unmapped --score_min L,0,-0.2 --temp_dir temp/ --bowtie2 $BisRef_path -o . -1 ${sampleID}_R1.clean.fastq.gz -2 ${sampleID}_R2.clean.fastq.gz >bismark.log

#去除重复
echo '#########################markdup#########################'
echo '#########################markdup#########################' >> cmd.log
echo $sambamba view --format=bam -h -t $thread -F "mapping_quality>=10" -o ${sampleID}_R1.f.bam ${sampleID}_R1.clean_bismark_bt2_pe.bam >> cmd.log
echo $sambamba markdup -r -t $thread ${sampleID}_R1.f.bam ${sampleID}.f.dedup.bam >> cmd.log
echo $Bisextractor --gzip --bedGraph --no_overlap --parallel $thread ${sampleID}.f.dedup.bam -o meth_result >> cmd.log

$sambamba view --format=bam -h -t $thread -F "mapping_quality>=10" -o ${sampleID}_R1.f.bam ${sampleID}_R1.clean_bismark_bt2_pe.bam
$sambamba markdup -r -t $thread ${sampleID}_R1.f.bam ${sampleID}.f.dedup.bam
$Bisextractor --gzip --bedGraph --no_overlap --parallel $thread ${sampleID}.f.dedup.bam -o meth_result

#bam排序
echo '#########################sorted##########################'
echo '#########################sorted##########################' >> cmd.log
echo $sambamba sort -t $thread -o ${sampleID}_R1.f.dedup.sorted.bam ${sampleID}.f.dedup.bam >> cmd.log
$sambamba sort -t $thread -o ${sampleID}_R1.f.dedup.sorted.bam ${sampleID}.f.dedup.bam

#加上头注释
echo '#########################AddGroups#######################'
echo '#########################AddGroups#######################' >> cmd.log
java -jar $AddGroups I=${sampleID}_R1.f.dedup.sorted.bam O=${sampleID}_R1.f.dedup.sorted.re.bam RGID=$sampleID RGLB=$sampleID RGPL=illumina RGSM=$sampleID RGPU=METHY
echo java -jar $AddGroups I=${sampleID}_R1.f.dedup.sorted.bam O=${sampleID}_R1.f.dedup.sorted.re.bam RGID=$sampleID RGLB=$sampleID RGPL=illumina RGSM=$sampleID RGPU=METHY >> cmd.log

#深度覆盖度测量
echo '#########################DepthOfCoverage#################'
echo '#########################DepthOfCoverage#################' >> cmd.log
$samtools index ${sampleID}_R1.f.dedup.sorted.re.bam
echo $gatk DepthOfCoverage -I ${sampleID}_R1.f.dedup.sorted.re.bam -L $bed_file -O ${sampleID}.coverage -R $ref_fasta >> cmd.log
$gatk DepthOfCoverage -I ${sampleID}_R1.f.dedup.sorted.re.bam -L $bed_file -O ${sampleID}.coverage -R $ref_fasta >DepthOfCoverage.log

#统计覆盖情况
echo '#########################CalculateHsMetrics##############'
echo '#########################CalculateHsMetrics##############' >> cmd.log
java -jar $CalculateHsMetrics INPUT= ${sampleID}_R1.f.dedup.sorted.re.bam BI=${interval_file} TI=${interval_file} OUTPUT=${sampleID}_R1_dedup.picard.cov.txt REFERENCE_SEQUENCE=$ref_fasta VALIDATION_STRINGENCY=LENIENT PER_TARGET_COVERAGE=${sampleID}.coverage
echo java -jar $CalculateHsMetrics INPUT= ${sampleID}_R1.f.dedup.sorted.re.bam BI=${interval_file} TI=${interval_file} OUTPUT=${sampleID}_R1_dedup.picard.cov.txt REFERENCE_SEQUENCE=$ref_fasta VALIDATION_STRINGENCY=LENIENT PER_TARGET_COVERAGE=${sampleID}.coverage >> cmd.log
java -jar $CalculateHsMetrics INPUT= ${sampleID}_R1.f.bam BI=${interval_file} TI=${interval_file} OUTPUT=${sampleID}_R1.picard.cov.txt REFERENCE_SEQUENCE=$ref_fasta VALIDATION_STRINGENCY=LENIENT PER_TARGET_COVERAGE=${sampleID}.coverage
echo java -jar $CalculateHsMetrics INPUT= ${sampleID}_R1.f.bam BI=${interval_file} TI=${interval_file} OUTPUT=${sampleID}_R1.picard.cov.txt REFERENCE_SEQUENCE=$ref_fasta VALIDATION_STRINGENCY=LENIENT PER_TARGET_COVERAGE=${sampleID}.coverage >> cmd.log

#统计最终结构
echo '########################stat info########################'
python3 $script_path/meth_info.py $sampleID > stat_result.txt
echo $sampleID finish at time `date +%F'  '%H:%M:%S`
